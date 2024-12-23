import json as native_json
import os
import socket
import time

import requests

from britive.exceptions.badrequest import bad_request_code_map
from britive.exceptions.generic import generic_code_map
from britive.exceptions.unauthorized import unauthorized_code_map

from . import __version__
from .access_broker import AccessBroker
from .application_management import ApplicationManagement
from .audit_logs import AuditLogs
from .exceptions import (
    BritiveException,
    InvalidFederationProvider,
    RootEnvironmentGroupNotFound,
    TenantMissingError,
    TenantUnderMaintenance,
    TokenMissingError,
    allowed_exceptions,
)
from .federation_providers import (
    AwsFederationProvider,
    AzureSystemAssignedManagedIdentityFederationProvider,
    AzureUserAssignedManagedIdentityFederationProvider,
    BitbucketFederationProvider,
    GithubFederationProvider,
    GitlabFederationProvider,
    SpaceliftFederationProvider,
)
from .global_settings import GlobalSettings
from .helpers import HelperMethods as helper_methods
from .identity_management import IdentityManagement
from .my_access import MyAccess
from .my_approvals import MyApprovals
from .my_requests import MyRequests
from .my_resources import MyResources
from .my_secrets import MySecrets
from .reports.reports import Reports
from .secrets_manager.secrets_manager import SecretsManager
from .security import ApiTokens, Security
from .system import System
from .workflows import Workflows


class Britive:
    """
    Pure Python implementation for interacting with the Britive API.

    The end user should never need to use any other classes in this package. Everything is accessed via this `Britive`
    class.

    This package aims to wrap the Britive API for use in Python. For the most part it is a simple wrapper (sending
    potentially bad parameters to the API) but there are a couple of places where liberties were taken to enhance
    the developer/end user experience. Some APIs may also be combined into one Python method with a parameter if and
    where it makes more sense to present the API that way.

    Authentication is handled solely via API tokens. The token must be provided in one of two methods.

    - Passed directly into the class constructor.
    - Injected as an environment variable into the execution context where this package is being run. The
       environment variable name must be BRITIVE_API_TOKEN.

    As of v2.5.0 a `Bearer` token can be provided as well. A `Bearer` token is generated as part of an interactive
    login process and is temporary in nature. This change is to allow for an upcoming Python CLI application.

    All Britive API tokens are authenticated against a specific Britive tenant. The name of the tenant must be provided
    in one of two methods.

    - Passed directly into the class constructor.
    - Injected as an environment variable into the execution context where this package is being run. The
       environment variable name must be BRITIVE_TENANT.

    In order to obtain the tenant name, reference the Britive URL used to login to the UI. If the URL is
    https://example.britive-app.com then the tenant name will be `example`.

    No assumptions are made about the operating system or file system. Nothing is persisted to disk. The end user
    must persist responses to disk if and when that is required.
    """

    def __init__(
        self,
        tenant: str = None,
        token: str = None,
        query_features: bool = True,
        token_federation_provider: str = None,
        token_duration: int = 900,
    ) -> None:
        """
        Instantiate an authenticated interface that can be used to communicate with the Britive API.

        :param tenant: The name of the Britive tenant. If the url you use to login to your Britive tenant is
            https://example.britive-app.com then your tenant name is `example` and is what you would provide here.
            If not provided then environment variable BRITIVE_TENANT will be used.
        :param token: The API token. If not provided then environment variable BRITIVE_API_TOKEN will be used.
        :param query_features: Indicates whether the SDK will query for features of the tenant (things like profile v1
            vs v2, secrets manager enabled,etc.). True by default but can be disabled as needed if the end user does not
            want to wait for that API call. Querying for features will help instruct the SDK as to what API calls are
            allowed to be used based on the features enabled, vs. attempting to make the API call and getting an error.
        :param token_federation_provider: The federation provider to use to source the token. Details of what can be
            provided can be found in the documentation for the Britive.source_federation_token_from method.
        :param token_federation_provider_duration_seconds: Only applicable for the AWS provider. Specify the number of
            seconds for which the generated token is valid. Defaults to 900 seconds (15 minutes).
        :raises: TenantMissingError, TokenMissingError
        """

        self.tenant = tenant or os.getenv('BRITIVE_TENANT')
        if not self.tenant:
            raise TenantMissingError('Tenant not provided and cannot be sourced from environment.')

        self.__token = self._initialize_token(token, token_federation_provider, token_duration)
        self.base_url = f'https://{self.parse_tenant(self.tenant)}/api'
        self.session = self._setup_session()

        self.retry_backoff_factor = 1
        self.retry_max_times = 5
        self.retry_response_status = {429, 500, 502, 503, 504}

        self._initialize_components(query_features)

    def _initialize_token(self, token: str, provider: str, duration: int) -> str:
        if provider:
            return self.source_federation_token_from(provider, self.tenant, duration)
        return token or os.getenv('BRITIVE_API_TOKEN') or TokenMissingError('Token not provided.')

    def _setup_session(self) -> requests.Session:
        session = requests.Session()

        # if PYBRITIVE_CA_BUNDLE set, in pybritive most likely, use it
        if britive_ca_bundle := os.getenv('PYBRITIVE_CA_BUNDLE'):
            session.verify = britive_ca_bundle

        # allow the disabling of TLS/SSL verification for testing in development (mostly local development)
        if os.getenv('BRITIVE_NO_VERIFY_SSL') and '.dev.' in self.tenant:
            session.verify = False
            self._disable_ssl_verification_warnings()

        token_type = self._determine_token_type()
        version = __version__

        session.headers.update(
            {
                'Authorization': f'{token_type} {self.__token}',
                'Content-Type': 'application/json',
                'User-Agent': f'britive-python-sdk/{version} {requests.utils.default_user_agent()}',
            }
        )
        return session

    def _disable_ssl_verification_warnings(self) -> None:
        # wipe these due to this bug: https://github.com/psf/requests/issues/3829
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _determine_token_type(self) -> str:
        if len(self.__token) < 50:
            return 'TOKEN'
        if len(self.__token.split('::')) > 1:
            return 'WorkloadToken'
        return 'Bearer'

    def _initialize_components(self, query_features: bool) -> None:
        self.access_broker = AccessBroker(self)
        self.api_tokens = ApiTokens(self)
        self.feature_flags = self.features() if query_features else {}
        self.my_access = MyAccess(self)
        self.my_approvals = MyApprovals(self)
        self.my_requests = MyRequests(self)
        self.my_resources = MyResources(self)
        self.my_secrets = MySecrets(self)
        self.reports = Reports(self)
        self.secrets_manager = SecretsManager(self)
        self.system = System(self)

        self.application_management = ApplicationManagement(self)
        self.audit_logs = AuditLogs(self)
        self.identity_management = IdentityManagement(self)
        self.global_settings = GlobalSettings(self)
        self.security = Security(self)
        self.workflows = Workflows(self)

        # FUTURE_BRITIVE_SDK == 'true' will remove backwards compatibility
        if os.getenv('FUTURE_BRITIVE_SDK', 'false').lower() != 'true':
            self.access_builder = self.application_management.access_builder
            self.accounts = self.application_management.accounts
            self.applications = self.application_management.applications
            self.audit_logs.logs.webhooks = self.audit_logs.webhooks
            self.audit_logs = self.audit_logs.logs
            self.environment_groups = self.application_management.environment_groups
            self.environments = self.application_management.environments
            self.groups = self.application_management.groups
            self.identity_attributes = self.identity_management.identity_attributes
            self.identity_providers = self.identity_management.identity_providers
            self.notification_mediums = self.global_settings.notification_mediums
            self.notifications = self.workflows.notifications
            self.permissions = self.application_management.permissions
            self.profiles = self.application_management.profiles
            self.saml = self.security.saml
            self.scans = self.application_management.scans
            self.security_policies = self.security.security_policies
            self.service_identities = self.identity_management.service_identities
            self.service_identity_tokens = self.identity_management.service_identity_tokens
            self.step_up = self.security.step_up_auth
            self.tags = self.identity_management.tags
            self.task_services = self.workflows.task_services
            self.tasks = self.workflows.tasks
            self.users = self.identity_management.users
            self.workload = self.identity_management.workload
            self.settings = self.global_settings

    @staticmethod
    def source_federation_token_from(provider: str, tenant: str = None, duration_seconds: int = 900) -> str:
        """
        Returns a token from the specified federation provider.

        The caller must persist this token if required. New tokens can be generated on each invocation
        of this class as well.

        This method only works when running within the context of the specified provider.
        It is meant to abstract away the complexities of obtaining a federation token
        from common federation providers. Other provider federation tokens can still be
        sourced outside of this SDK and provided as input via the standard token presentation
        options.

        Six federation providers are currently supported by this method.

        * AWS IAM/STS, with optional profile specified - (aws)
        * Azure System Assigned Managed Identities (azuresmi)
        * Azure User Assigned Managed Identities (azureumi)
        * Bitbucket Pipelines (bitbucket)
        * Github Actions (github)
        * Gitlab (gitlab)
        * spacelift.io (spacelift)

        Any other OIDC federation provider can be used and tokens can be provided to this class for authentication
        to a Britive tenant. Details of how to construct these tokens can be found at https://docs.britive.com.

        :param provider: The name of the federation provider. Valid options are `aws`, `github`, `bitbucket`,
            `azuresmi`, `azureumi`, `spacelift`, and `gitlab`.

            For the AWS provider it is possible to provide a profile via value `aws-profile`. If no profile is provided
            then the boto3 `Session.get_credentials()` method will be used to obtain AWS credentials, which follows
            the order provided here:
            https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#configuring-credentials

            For Azure User Assigned Managed Identities (azureumi) a client id is required. It must be
            provided in the form `azureumi-<client-id>`. From the Azure documentation...a user-assigned identity's
            client ID or, when using Pod Identity, the client ID of an Azure AD app registration. This argument
            is supported in all hosting environments.

            For both Azure Managed Identity options it is possible to provide an OIDC audience value via
            `azuresmi-<audience>` and `azureumi-<client-id>|<audience>`. If no audience is provided the default audience
             of `https://management.azure.com/` will be used.

            For the Github provider it is possible to provide an OIDC audience value via `github-<audience>`. If no
            audience is provided the default Github audience value will be used.

            For the Gitlab provider a token environment variable name can optionally be specified via `gitlab-ENV_VAR`.
            Anything after `gitlab-` will be interpreted to represent the name of the environment variable specified
            in the YAML file for the ID token. If not provided it will default to `BRITIVE_OIDC_TOKEN`.

        :param tenant: The name of the tenant. This field is optional but if not provided then the tenant will be
            sourced from environment variable BRITIVE_TENANT. Knowing the actual tenant is required for the AWS
            federation provider. This field can be ignored for non AWS federation providers.
        :param duration_seconds: Only applicable for the AWS provider. Specify the number of seconds for which the
            generated token is valid. Defaults to 900 seconds (15 minutes).
        :return: A federation token that can be used to authenticate to a Britive tenant.
        """

        helper = provider.split('-', maxsplit=1)
        provider_name = helper[0]

        federation_providers = {
            'aws': lambda: AwsFederationProvider(
                profile=helper_methods.safe_list_get(helper, 1), tenant=tenant, duration=duration_seconds
            ).get_token(),
            'bitbucket': lambda: BitbucketFederationProvider().get_token(),
            'github': lambda: GithubFederationProvider(audience=helper_methods.safe_list_get(helper, 1)).get_token(),
            'gitlab': lambda: GitlabFederationProvider(
                token_env_var=helper_methods.safe_list_get(helper, 1)
            ).get_token(),
            'spacelift': lambda: SpaceliftFederationProvider().get_token(),
        }

        if provider_name in federation_providers:
            return federation_providers[provider_name]()

        if provider_name == 'azuresmi':
            return AzureSystemAssignedManagedIdentityFederationProvider(
                audience=helper_methods.safe_list_get(helper, 1)
            ).get_token()

        if provider_name == 'azureumi':
            return AzureUserAssignedManagedIdentityFederationProvider(
                client_id=helper[1].split('|')[0], audience=helper_methods.safe_list_get(helper[1].split('|'), 1)
            ).get_token()

        raise InvalidFederationProvider(f'federation provider {provider_name} not supported')

    @staticmethod
    def parse_tenant(tenant: str) -> str:
        domain = tenant.replace('https://', '').replace('http://', '').split('/')[0]  # remove scheme and paths
        try:
            socket.getaddrinfo(host=domain, port=443)  # if success then a full domain was provided
            return domain
        except socket.gaierror:  # assume just the tenant name was provided (originally the only supported method)
            resolved_domain = f'{tenant}.britive-app.com'
            try:
                socket.getaddrinfo(host=resolved_domain, port=443)  # validate the hostname is real
                return resolved_domain  # and if so set the tenant accordingly
            except socket.gaierror as e:
                raise Exception(f'Invalid tenant provided: {tenant}. DNS resolution failed.') from e

    def features(self) -> dict:
        return {feature['name']: feature['enabled'] for feature in self.get(f'{self.base_url}/features')}

    def banner(self) -> dict:
        return self.get(f'{self.base_url}/banner')

    def get(self, url, params=None) -> dict:
        """Internal use only."""

        return self.__request('get', url, params=params)

    def post(self, url, params=None, data=None, json=None) -> dict:
        """Internal use only."""

        return self.__request('post', url, params=params, data=data, json=json)

    def patch(self, url, params=None, data=None, json=None) -> dict:
        """Internal use only."""

        return self.__request('patch', url, params=params, data=data, json=json)

    def put(self, url, params=None, data=None, json=None) -> dict:
        """Internal use only."""

        return self.__request('put', url, params=params, data=data, json=json)

    def delete(self, url, params=None, data=None, json=None) -> dict:
        """Internal use only."""

        return self.__request('delete', url, params=params, data=data, json=json)

    # note - this method could be iffy in the future if the app changes the way it handles
    # file uploads. As of 2022-01-26 it is working fine with the "Upload SAML Metadata" action
    # of an identity provider. This is the only use case currently.
    def patch_upload(self, url, file_content_as_str, content_type, filename) -> dict:
        """Internal use only."""

        files = {filename: (f'{filename}.xml', file_content_as_str, content_type)}
        response = self.session.patch(url, files=files, headers={'Content-Type': None})
        return self._handle_response(response)

    # note - this method is only used to upload a file when creating a secret
    def post_upload(self, url, params=None, files=None) -> dict:
        """Internal use only."""

        response = self.session.post(url, params=params, files=files, headers={'Content-Type': None})
        return self._handle_response(response)

    @staticmethod
    def _handle_response(response):
        try:
            return response.json()
        # Can likely drop to just the `requests` exception, with `>=2.32.0`, but leaving both for now.
        except (native_json.decoder.JSONDecodeError, requests.exceptions.JSONDecodeError):
            return response.content.decode('utf-8')

    @staticmethod
    def __check_response_for_error(status_code, content) -> None:
        if status_code in allowed_exceptions:
            if isinstance(content, dict):
                error_code = content.get('errorCode', 'E0000')
                message = f"{status_code} - {error_code} - {content.get('message', 'no message available')}"
                if content.get('details'):
                    message += f" - {content.get('details')}"
            else:
                message = f'{status_code} - {content}'
            raise unauthorized_code_map.get(
                error_code,
                bad_request_code_map.get(
                    error_code,
                    generic_code_map.get(error_code, allowed_exceptions.get(status_code, BritiveException)),
                ),
            )(message)

    @staticmethod
    def __response_has_no_content(response) -> bool:
        # handle 204 No Content response
        return response.status_code in (204,) or (response.status_code == 200 and len(response.content) == 0)

    @staticmethod
    def __pagination_type(headers, result) -> str:
        is_dict = isinstance(result, dict)
        has_next_page_header = 'next-page' in headers

        if is_dict and all(x in result for x in ('count', 'page', 'size', 'data')):
            return 'inline'
        if is_dict and has_next_page_header and all(x in result for x in ('data', 'reportId')):  # reports
            return 'report'
        if has_next_page_header:  # this interesting way of paginating is how audit_logs.query() does it
            return 'audit'
        if is_dict and all(x in result for x in ('result', 'pagination')):
            return 'secmgr'
        return 'none'

    @staticmethod
    def __tenant_is_under_maintenance(response) -> bool:
        return response.status_code == 503 and response.json().get('errorCode') == 'MAINT0001'

    def __request_with_exponential_backoff_and_retry(self, method, url, params, data, json) -> dict:
        num_retries = 0

        while num_retries <= self.retry_max_times:
            response = self.session.request(method, url, params=params, data=data, json=json)

            # handle the use case of a tenant being in maintenance mode
            # which means we should break out of this loop early and
            # not perform the backoff and retry logic
            if self.__tenant_is_under_maintenance(response):
                raise TenantUnderMaintenance(response.json().get('message'))

            if response.status_code in self.retry_response_status:
                time.sleep((2**num_retries) * self.retry_backoff_factor)
                num_retries += 1
            else:
                self.__check_response_for_error(response.status_code, self._handle_response(response))
                return response

    def __request(self, method, url, params=None, data=None, json=None) -> dict:
        return_data = []
        pagination_type = None

        while True:
            response = self.__request_with_exponential_backoff_and_retry(method, url, params, data, json)
            if self.__response_has_no_content(response):
                return None

            # handle secrets file download
            content_disposition = response.headers.get('content-disposition', '').lower()
            if 'attachment' in content_disposition and 'downloadfile' in url:
                filename = response.headers['content-disposition'].split('=')[1].replace('"', '').strip()
                return {'filename': filename, 'content_bytes': bytes(response.content)}

            # load the result as a dict
            result = self._handle_response(response)
            pagination_type = pagination_type or self.__pagination_type(response.headers, result)

            # check on the pagination and iterate if required - we only need to check on this after the first
            # request - checking it each time can screw up the logic when dealing with pagination coming from
            # the response headers as the header won't exist which will mean pagination_type will change to 'none'
            # which means we drop into the else block below and assign just the LAST page as the result, which
            # is obviously not what we want to be doing.
            if pagination_type == 'inline':
                return_data += result['data']
                if result['size'] * (result['page'] + 1) >= result['count']:
                    break
                params['page'] = result['page'] + 1
            elif pagination_type in ('audit', 'report'):
                return_data += result if pagination_type == 'audit' else result['data']
                if 'next-page' not in response.headers:
                    break
                url = response.headers['next-page']
                params = {}
            elif pagination_type == 'secmgr':
                return_data += result['result']
                url = result['pagination'].get('next', '')
                if not url:
                    break
            else:
                return_data = result
                break

        return return_data

    def get_root_environment_group(self, application_id: str) -> str:
        """Internal use only."""

        app = self.application_management.applications.get(application_id=application_id)
        root_env_group = app.get('rootEnvironmentGroup', {}).get('environmentGroups', [])
        for group in root_env_group:
            if not group['parentId']:
                return group['id']
        raise RootEnvironmentGroupNotFound()
