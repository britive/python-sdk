import os

from britive.exceptions import NotExecutingInBitbucketEnvironment

from .federation_provider import FederationProvider


class BitbucketFederationProvider(FederationProvider):
    def __init__(self) -> None:
        super().__init__()

    def get_token(self) -> str:
        id_token = os.environ.get('BITBUCKET_STEP_OIDC_TOKEN')
        if not id_token:
            msg = (
                'the codebase is not executing in a bitbucket environment and/or the `oidc` flag '
                'is not set on the pipeline step'
            )
            raise NotExecutingInBitbucketEnvironment(msg)
        return f'OIDC::{id_token}'
