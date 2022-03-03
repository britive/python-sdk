"""
This code has been pulled from the API wrapper in favor of only allowing API tokens.
It is being stored here for future potential use in other Britive python tooling.
"""

import random
import base64
import hashlib
import webbrowser
import time
import requests


class InteractiveLoginTimeout(Exception):
    pass


def b64_encode_url_safe(value: bytes):
    return base64.urlsafe_b64encode(value).decode('utf-8').replace('=', '')


def __interactive_login(self):
    # not sure if we really need 32 random bytes or if any random string would work
    # but the current britive-cli in node.js does it this way so it will be done the same
    # way in python
    self.verifier = b64_encode_url_safe(bytes([random.getrandbits(8) for _ in range(0, 32)]))
    auth_token = b64_encode_url_safe(bytes(hashlib.sha512(self.verifier.encode('utf-8')).digest()))
    url = f'https://{self.tenant}.britive-app.com/login?token={auth_token}'
    webbrowser.get().open(url)
    time.sleep(3)
    num_tries = 1
    while True:
        if num_tries > 60:
            raise InteractiveLoginTimeout()
        response = self.__retrieve_tokens()

        if response.status_code >= 400:
            time.sleep(2)
            num_tries += 1
        else:
            token = response.json()['authenticationResult']['accessToken']
            self.__token = token  # TODO - persist this token to ~/.britive/credentials
            break


def __retrieve_tokens(self):
    url = f'{self.base_url}/auth/cli/retrieve-tokens'
    auth_params = {
        'authParameters': {
            'cliToken': self.verifier
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    return requests.post(url, headers=headers, json=auth_params)
