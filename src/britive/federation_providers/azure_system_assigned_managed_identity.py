from britive.exceptions import MissingAzureDependency, NotExecutingInAzureEnvironment

from .federation_provider import FederationProvider


class AzureSystemAssignedManagedIdentityFederationProvider(FederationProvider):
    def __init__(self, audience: str = None) -> None:
        self.audience = audience if audience else 'https://management.azure.com/'
        super().__init__()

    def get_token(self) -> str:
        try:
            from azure.identity import ManagedIdentityCredential
            from azure.identity._exceptions import CredentialUnavailableError

            token = ManagedIdentityCredential().get_token(self.audience).token
            return f'OIDC::{token}'
        except ImportError as e:
            raise MissingAzureDependency(
                '`azure-identity` package required to use the azure managed identity federation provider'
            ) from e
        except CredentialUnavailableError as e:
            msg = (
                'the codebase is not executing in an Azure environment or some other issue is causing the '
                'managed identity credentials to be unavailable'
            )
            raise NotExecutingInAzureEnvironment(msg) from e
