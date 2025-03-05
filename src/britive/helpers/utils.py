import socket
from typing import Optional, Union

import requests

from britive.exceptions import BritiveException, InvalidFederationProvider, allowed_exceptions
from britive.exceptions.badrequest import bad_request_code_map
from britive.exceptions.generic import generic_code_map
from britive.exceptions.unauthorized import InvalidTenantError, unauthorized_code_map
from britive.federation_providers import (
    AwsFederationProvider,
    AzureSystemAssignedManagedIdentityFederationProvider,
    AzureUserAssignedManagedIdentityFederationProvider,
    BitbucketFederationProvider,
    GithubFederationProvider,
    GitlabFederationProvider,
    SpaceliftFederationProvider,
)


def check_response_for_error(status_code, content) -> None:
    if status_code in allowed_exceptions:
        if isinstance(content, dict):
            error_code = content.get('errorCode', 'E0000')
            message = f'{status_code} - {error_code} - {content.get("message", "no message available")}'
            if content.get('details'):
                message += f' - {content.get("details")}'
        else:
            message = f'{status_code} - {content}'
        raise unauthorized_code_map.get(
            error_code,
            bad_request_code_map.get(
                error_code,
                generic_code_map.get(error_code, allowed_exceptions.get(status_code, BritiveException)),
            ),
        )(message)


def handle_response(response):
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return response.content.decode('utf-8')


def pagination_type(headers, result) -> str:
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
            raise InvalidTenantError(f'Invalid tenant provided: {tenant}. DNS resolution failed.') from e


def response_has_no_content(response) -> bool:
    # handle 204 No Content response
    return response.status_code in (204,) or (response.status_code == 200 and len(response.content) == 0)


def safe_list_get(lst: list, idx: int, default: str = None) -> Union[str, None]:
    try:
        return lst[idx]
    except IndexError:
        return default


def source_federation_token(provider: str, tenant: Optional[str] = None, duration_seconds: int = 900) -> str:
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
            profile=safe_list_get(helper, 1), tenant=tenant, duration=duration_seconds
        ).get_token(),
        'bitbucket': lambda: BitbucketFederationProvider().get_token(),
        'github': lambda: GithubFederationProvider(audience=safe_list_get(helper, 1)).get_token(),
        'gitlab': lambda: GitlabFederationProvider(token_env_var=safe_list_get(helper, 1)).get_token(),
        'spacelift': lambda: SpaceliftFederationProvider().get_token(),
    }

    if provider_name in federation_providers:
        return federation_providers[provider_name]()

    if provider_name == 'azuresmi':
        return AzureSystemAssignedManagedIdentityFederationProvider(audience=safe_list_get(helper, 1)).get_token()

    if provider_name == 'azureumi':
        return AzureUserAssignedManagedIdentityFederationProvider(
            client_id=helper[1].split('|')[0], audience=safe_list_get(helper[1].split('|'), 1)
        ).get_token()

    raise InvalidFederationProvider(f'federation provider {provider_name} not supported')


def tenant_is_under_maintenance(response) -> bool:
    return response.status_code == 503 and response.json().get('errorCode') == 'MAINT0001'
