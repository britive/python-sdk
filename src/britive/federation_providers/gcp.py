from britive.exceptions import MissingGcpDependency, NotExecutingInGcpEnvironment

from .federation_provider import FederationProvider


class GcpFederationProvider(FederationProvider):
    def __init__(self, audience: str = None) -> None:
        self.audience = audience if audience else 'https://accounts.google.com/'
        super().__init__()

    def get_token(self):
        try:
            from google.auth.exceptions import DefaultCredentialsError
            from google.auth.transport.requests import Request
            from google.oauth2 import id_token

            token = id_token.fetch_id_token(Request(), self.audience)

            return f'OIDC::{token}'
        except ImportError as e:
            raise MissingGcpDependency(
                'google dependency package required to use the gcp managed identity federation provider, '
                'install with `pip install britive[gcp]'
            ) from e
        except DefaultCredentialsError as e:
            msg = (
                'the codebase is not executing in an Gcp environment or some other issue is causing the '
                'managed identity credentials to be unavailable'
            )
            raise NotExecutingInGcpEnvironment(msg) from e
