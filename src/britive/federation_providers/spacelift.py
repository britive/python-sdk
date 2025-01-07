import os

from britive.exceptions import NotExecutingInSpaceliftEnvironment

from .federation_provider import FederationProvider


class SpaceliftFederationProvider(FederationProvider):
    def __init__(self) -> None:
        super().__init__()

    # https://docs.spacelift.io/integrations/cloud-providers/oidc/
    def get_token(self) -> str:
        id_token = os.environ.get('SPACELIFT_OIDC_TOKEN')
        if not id_token:
            msg = 'the codebase is not executing in a spacelift.io environment or not using a paid account'
            raise NotExecutingInSpaceliftEnvironment(msg)
        return f'OIDC::{id_token}'
