import os

import requests

from britive.exceptions import NotExecutingInGithubEnvironment

from .federation_provider import FederationProvider


class GithubFederationProvider(FederationProvider):
    def __init__(self, audience: str = None) -> None:
        self.audience = audience
        super().__init__()

    def get_token(self) -> str:
        url = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL')
        bearer_token = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN')

        if not url or not bearer_token:
            msg = (
                'the codebase is not executing in a github environment and/or the action is '
                'not set to use oidc permissions'
            )
            raise NotExecutingInGithubEnvironment(msg)

        headers = {'User-Agent': 'actions/oidc-client', 'Authorization': f'Bearer {bearer_token}'}

        if self.audience:
            url += f'&audience={self.audience}'

        response = requests.get(url, headers=headers)
        return f'OIDC::{response.json()["value"]}'
