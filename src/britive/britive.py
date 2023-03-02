import os
import requests
from requests.adapters import HTTPAdapter, Retry
import json as native_json
import pkg_resources
import socket
from .helpers import methods as helper_methods
from .helpers import federation_providers as fp
from .users import Users
from .service_identity_tokens import ServiceIdentityTokens
from .service_identities import ServiceIdentities
from .exceptions import *
from .tags import Tags
from .applications import Applications
from .environments import Environments
from .environment_groups import EnvironmentGroups
from .scans import Scans
from .accounts import Accounts
from .permissions import Permissions
from .groups import Groups
from .identity_attributes import IdentityAttributes
from .profiles import Profiles
from .task_services import TaskServices
from .tasks import Tasks
from .security_policies import SecurityPolicies
from .saml import Saml
from .api_tokens import ApiTokens
from .audit_logs import AuditLogs
from .reports import Reports
from .identity_providers import IdentityProviders
from .my_access import MyAccess
from .notifications import Notifications
from .my_secrets import MySecrets
from .policies import  Policies
from .secrets_manager import SecretsManager
from .notification_mediums import NotificationMediums


BRITIVE_TENANT_ENV_NAME = 'BRITIVE_TENANT'
BRITIVE_TOKEN_ENV_NAME = 'BRITIVE_API_TOKEN'


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

    def __init__(self, tenant: str = None, token: str = None, query_features: bool = True,
                 token_federation_provider: str = None, token_federation_provider_duration_seconds: int = 900):
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

        self.tenant = tenant or os.environ.get(BRITIVE_TENANT_ENV_NAME)

        if token_federation_provider:
            self.__token = self.source_federation_token_from(
                provider=token_federation_provider,
                duration_seconds=token_federation_provider_duration_seconds
            )
        else:
            self.__token = token or os.environ.get(BRITIVE_TOKEN_ENV_NAME)

        if not self.tenant:
            raise TenantMissingError(
                'Tenant not explicitly provided and could not be sourced '
                f'from environment variable {BRITIVE_TENANT_ENV_NAME}'
            )

        if not self.__token:
            raise TokenMissingError(
                'Token not explicitly provided and could not be sourced '
                f'from environment variable {BRITIVE_TOKEN_ENV_NAME}'
            )

        # clean up and apply logic to the passed in tenant (for backwards compatibility with no domain being required)
        self.tenant = self.parse_tenant(self.tenant)

        self.base_url = f'https://{self.tenant}/api'
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        # allow the disabling of TLS/SSL verification for testing in development (mostly local development)
        if os.getenv('BRITIVE_NO_VERIFY_SSL') and '.dev.' in self.tenant:
            # turn off ssl verification
            self.session.verify = False
            # wipe these due to this bug: https://github.com/psf/requests/issues/3829
            os.environ['CURL_CA_BUNDLE'] = ""
            os.environ['REQUESTS_CA_BUNDLE'] = ""
            # disable the warning message
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        token_type = 'TOKEN' if len(self.__token) < 50 else 'Bearer'
        if len(self.__token.split('::')) > 1:
            token_type = 'WorkloadToken'

        try:
            version = pkg_resources.get_distribution('britive').version
        except Exception:
            version = 'unknown'

        self.session.headers.update({
            'Authorization': f'{token_type} {self.__token}',
            'Content-Type': 'application/json',
            'User-Agent': f'britive-python-sdk/{version} {requests.utils.default_user_agent()}'
        })

        self.feature_flags = self.features() if query_features else {}

        self.users = Users(self)
        self.service_identity_tokens = ServiceIdentityTokens(self)
        self.service_identities = ServiceIdentities(self)
        self.tags = Tags(self)
        self.applications = Applications(self)
        self.environments = Environments(self)
        self.environment_groups = EnvironmentGroups(self)
        self.scans = Scans(self)
        self.accounts = Accounts(self)
        self.permissions = Permissions(self)
        self.groups = Groups(self)
        self.identity_attributes = IdentityAttributes(self)
        self.profiles = Profiles(self, 1 if self.feature_flags.get('profile-v1') else 2)
        self.task_services = TaskServices(self)
        self.tasks = Tasks(self)
        self.security_policies = SecurityPolicies(self)
        self.saml = Saml(self)
        self.api_tokens = ApiTokens(self)
        self.audit_logs = AuditLogs(self)
        self.reports = Reports(self)
        self.identity_providers = IdentityProviders(self)
        self.my_access = MyAccess(self)
        self.notifications = Notifications(self)
        self.my_secrets = MySecrets(self)
        self.policies = Policies(self)
        self.secrets_manager = SecretsManager(self)
        self.notification_mediums = NotificationMediums(self)

    @staticmethod
    def source_federation_token_from(provider: str, tenant: str = None, duration_seconds: int = 900) -> str:
        """
        Returns a token from the specified federation provider.

        The caller must persist this token if required. New tokens can be generated on each invocation
        of this class as well.

        This method only works when running with the context of the specified provider.
        It is meant to abstract away the complexities of obtaining a federation token
        from common federation providers. Other provider federation tokens can still be
        sourced outside of this SDK and provided as input via the standard token presentation
        options.

        Five federation providers are currently supported by this method.

        * AWS IAM/STS, with optional profile specified - (aws)
        * Github Actions (github)
        * Bitbucket Pipelines (bitbucket)
        * Azure System Assigned Managed Identities (azuresmi)
        * Azure User Assigned Managed Identities (azureumi)

        Any other OIDC federation provider can be used and tokens can be provided to this class for authentication
        to a Britive tenant. Details of how to construct these tokens can be found at https://docs.britive.com.

        :param provider: The name of the federation provider. Valid options are `aws`, `github`, `bitbucket`,
            `azuresmi`, and `azureumi`.

            For the AWS provider it is possible to provide a profile via value `aws-profile`. If no profile is provided
            then the boto3 `Session.get_credentials()` method will be used to obtain AWS credentials, which follows
            the order provided here:
            https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#configuring-credentials

            For the Github provider it is possible to provide an OIDC audience value via `github-<audience>`. If no
            audience is provided the default Github audience value will be used.

            For Azure User Assigned Managed Identities (azureumi) a client id is required. It must be
            provided in the form `azureumi-<client-id>`. From the Azure documentation...a user-assigned identity's
            client ID or, when using Pod Identity, the client ID of an Azure AD app registration. This argument
            is supported in all hosting environments.

            For both Azure Managed Identity options it is possible to provide an OIDC audience value via
            `azuresmi-<audience>` and `azureumi-<client-id>|<audience>`. If no audience is provided the default audience
             of `https://management.azure.com/` will be used.

        :param tenant: The name of the tenant. This field is optional but if not provided then the tenant will be
            sourced from environment variable BRITIVE_TENANT. Knowing the actual tenant is required for the AWS
            federation provider. This field can be ignored for non AWS federation providers.
        :param duration_seconds: Only applicable for the AWS provider. Specify the number of seconds for which the
            generated token is valid. Defaults to 900 seconds (15 minutes).
        :return: A federation token that can be used to authenticate to a Britive tenant.
        """

        helper = provider.split('-', maxsplit=1)
        provider = helper[0]

        if provider == 'aws':
            profile = helper_methods.safe_list_get(helper, 1, None)
            return fp.AwsFederationProvider(
                profile=profile,
                tenant=tenant,
                duration=duration_seconds
            ).get_token()

        if provider == 'github':
            audience = helper_methods.safe_list_get(helper, 1, None)
            return fp.GithubFederationProvider(audience=audience).get_token()

        if provider == 'bitbucket':
            return fp.BitbucketFederationProvider().get_token()

        if provider == 'azuresmi':
            audience = helper_methods.safe_list_get(helper, 1, None)
            return fp.AzureSystemAssignedManagedIdentityFederationProvider(audience=audience).get_token()

        if provider == 'azureumi':
            additional_attributes_str = helper_methods.safe_list_get(helper, 1, None)
            if not additional_attributes_str:
                raise ValueError('client id is required via azurumi-<client-id>')
            additional_attributes = additional_attributes_str.split('|')
            client_id = additional_attributes[0]
            audience = helper_methods.safe_list_get(additional_attributes, 1, None)
            return fp.AzureUserAssignedManagedIdentityFederationProvider(
                client_id=client_id,
                audience=audience
            ).get_token()

        raise InvalidFederationProvider(f'federation provider {provider} not supported')

    @staticmethod
    def parse_tenant(tenant: str) -> str:
        domain = tenant.replace('https://', '').replace('http://', '')   # remove scheme
        domain = domain.split('/')[0]  # remove any paths as they will not be needed
        try:
            domain_helper = domain.split(':')
            port = 443
            if len(domain_helper) > 1:
                port = domain_helper[1]
            domain_without_port = domain_helper[0]
            socket.getaddrinfo(host=domain_without_port, port=port)  # if success then a full domain was provided
            return domain
        except socket.gaierror:  # assume just the tenant name was provided (originally the only supported method)
            domain = f'{tenant}.britive-app.com'
            try:
                socket.getaddrinfo(host=domain, port=443)  # validate the hostname is real
                return domain  # and if so set the tenant accordingly
            except socket.gaierror:
                raise Exception(f'Invalid tenant provided: {tenant}. DNS resolution failed.')

    def features(self):
        features = {}
        for feature in self.get(f'{self.base_url}/features'):
            features[feature['name']] = feature['enabled']
        return features

    def get(self, url, params=None):
        """Internal use only."""

        return self.__request('get', url, params=params)

    def post(self, url, params=None, data=None, json=None):
        """Internal use only."""

        return self.__request('post', url, params=params, data=data, json=json)

    def patch(self, url, params=None, data=None, json=None):
        """Internal use only."""

        return self.__request('patch', url, params=params, data=data, json=json)

    def put(self, url, params=None, data=None, json=None):
        """Internal use only."""

        return self.__request('put', url, params=params, data=data, json=json)

    def delete(self, url, params=None, data=None, json=None):
        """Internal use only."""

        return self.__request('delete', url, params=params, data=data, json=json)

    # note - this method could be iffy in the future if the app changes the way it handles
    # file uploads. As of 2022-01-26 it is working fine with the "Upload SAML Metadata" action
    # of an identity provider. This is the only use case currently.
    def patch_upload(self, url, file_content_as_str, content_type, filename):
        """Internal use only."""

        files = {
            filename: (f'{filename}.xml', file_content_as_str, content_type)
        }
        response = self.session.patch(url, files=files, headers={'Content-Type': None})
        try:
            return response.json()
        except native_json.decoder.JSONDecodeError:  # if we cannot decode json then the response isn't json
            return response.content.decode('utf-8')
    
    # note - this method is only used to upload a file when creating a secret
    def post_upload(self, url, params=None, files=None):
        """Internal use only."""
        response = self.session.post(url, params=params, files=files, headers={'Content-Type': None})
        try:
            return response.json()
        except native_json.decoder.JSONDecodeError:  # if we cannot decode json then the response isn't json
            return response.content.decode('utf-8')

    @staticmethod
    def __check_response_for_error(response):
        if response.status_code in allowed_exceptions.keys():
            try:
                content = native_json.loads(response.content.decode('utf-8'))
                message = f"{response.status_code} - " \
                          f"{content.get('errorCode') or 'E0000'} - " \
                          f"{content.get('message') or 'no message available'}"
                if content.get('details'):
                    message += f" - {content.get('details')}"
                raise allowed_exceptions[response.status_code](message)
            except native_json.decoder.JSONDecodeError as e:
                content = response.content.decode('utf-8')
                message = f"{response.status_code} - {content}"
                raise allowed_exceptions[response.status_code](message)

    @staticmethod
    def __response_has_no_content(response):
        # handle 204 No Content response
        if response.status_code == 204:
            return True

        # handle empty 200 response
        if response.status_code == 200 and len(response.content) == 0:
            return True

        return False

    @staticmethod
    def __pagination_type(headers, result):
        is_dict = isinstance(result, dict)
        has_next_page_header = 'next-page' in headers.keys()

        if is_dict and all(x in result.keys() for x in ['count', 'page', 'size', 'data']):
            return 'inline'
        if is_dict and has_next_page_header and all(x in result.keys() for x in ['data', 'reportId']):  # reports
            return 'report'
        if has_next_page_header:  # this interesting way of paginating is how audit_logs.query() does it
            return 'audit'
        if is_dict and all(x in result.keys() for x in ['result', 'pagination']):
            return 'secmgr'
        return 'none'

    def __request(self, method, url, params=None, data=None, json=None):
        return_data = []
        num_iterations = 1
        pagination_type = None
        while True:  # infinite loop in case of pagination - we will break the loop when needed
            response = self.session.request(method, url, params=params, data=data, json=json)
            self.__check_response_for_error(response)   # handle an error response
            if self.__response_has_no_content(response):  # handle no content responses
                return None

            # handle secrets file download
            lowercase_headers = {h.lower(): v.lower() for h, v in response.headers.items()}
            content_disposition = lowercase_headers.get('content-disposition', '')
            if 'attachment' in content_disposition and 'downloadfile' in url:
                filename = response.headers.get('content-disposition').split('=')[1].replace('"', '').strip()
                return {'filename': filename, 'content_bytes': bytes(response.content)}

            # load the result as a dict
            try:
                result = response.json()
            except ValueError:  # includes simplejson.decoder.JSONDecodeError and native_json.decoder.JSONDecodeError
                return response.content.decode('utf-8')

            # check on the pagination and iterate if required - we only need to check on this after the first
            # request - checking it each time can screw up the logic when dealing with pagination coming from
            # the response headers as the header won't exist which will mean pagination_type will change to 'none'
            # which means we drop into the else block below and assign just the LAST page as the result, which
            # is obviously not what we want to be doing.
            if num_iterations == 1:
                pagination_type = self.__pagination_type(response.headers, result)

            if pagination_type == 'inline':
                return_data += result['data']
                count = result['count']
                page = result['page']
                size = result['size']
                if size * (page + 1) >= count:  # if we have reached the max number of records time to break the loop
                    break
                else:  # else loop again after incrementing the page number by 1
                    params['page'] = page + 1
            elif pagination_type == 'audit':
                return_data += result  # result is already a list
                if 'next-page' not in response.headers.keys():
                    break
                url = response.headers['next-page']
                params = {}  # the next-page header has all the URL parameters we need so unset them here
            elif pagination_type == 'report':
                return_data += result['data']
                if 'next-page' not in response.headers.keys():
                    break
                url = response.headers['next-page']
                params = {}  # the next-page header has all the URL parameters we need so unset them here
            elif pagination_type == 'secmgr':
                return_data += result['result']
                next_page = result['pagination'].get('next', '')
                if next_page == '':
                    break
                else:
                    params['pageToken'] = next_page
            else:  # we are not dealing with pagination so just return the response as-is
                return_data = result
                break

            num_iterations += 1

        # finally return the response data
        return return_data

    def get_root_environment_group(self, application_id: str) -> str:
        """Internal use only."""

        app = self.applications.get(application_id=application_id)
        root_env_group = app.get('rootEnvironmentGroup') or {}
        for group in root_env_group.get('environmentGroups', []):
            if group['parentId'] == '':
                return group['id']
        raise RootEnvironmentGroupNotFound()

