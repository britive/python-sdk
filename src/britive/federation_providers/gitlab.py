import os

from britive.exceptions import NotExecutingInGitlabEnvironment

from .federation_provider import FederationProvider


class GitlabFederationProvider(FederationProvider):
    def __init__(self, token_env_var: str = 'BRITIVE_OIDC_TOKEN') -> None:
        super().__init__()
        self.token_env_var = token_env_var

    def get_token(self) -> str:
        id_token = os.environ.get(self.token_env_var)
        if not id_token:
            msg = (
                'the codebase is not executing in a gitlab environment or the incorrect token environment variable '
                'was specified'
            )
            raise NotExecutingInGitlabEnvironment(msg)
        return f'OIDC::{id_token}'
