from . import exceptions


class ApiTokens:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/token'

    def list(self) -> list:
        """
        Retrieve all API tokens in the system.

        :return: List of API tokens.
        """

        return self.britive.get(self.base_url)

    def get(self, token_id: str) -> dict:
        for token in self.list():
            if token['id'] == token_id:
                return token
        raise exceptions.ApiTokenNotFound()

    def create(self, name: str = None, expiration_days: int = 90) -> dict:
        """
        Create an API token with full administrator privileges.

        The token will only be returned in the response once. Future calls to `list` or `get` will not include the
        token value. Ensure the token returned from this method is stored or it will be unrecoverable.

        The token will be associated with the user identity that makes this API call.

        :param name: The name of the token.
        :param expiration_days: The number of days in which the token would expire since it was last used.
            Valid values are 1-90. Default is 90.
        :return: Details of the newly created token.
        """

        data = {
            'tokenExpirationDays': expiration_days
        }

        if name:
            data['name'] = name

        return self.britive.post(self.base_url, json=data)

    def revoke(self, token_id: str) -> None:
        """
        Revoke a token. Equivalent to deleting it.

        :param token_id: The ID of the token.
        :return: None
        """

        response = self.britive.delete(f'{self.base_url}/{token_id}')
        if response == 'Successfully revoked token':
            return None
        else:
            raise Exception(str(response))

    def delete(self, token_id: str) -> None:
        """
        Delete a token.

        Equivalent to revoking it. `delete` is provided for compatibility with other resource types.

        :param token_id: The ID of the token.
        :return: None
        """

        return self.revoke(token_id=token_id)

    def update(self, token_id: str, name: str = None, expiration_days: int = None) -> None:
        """
        Update a token.

        `name` and/or `expiration_days` needs to be provided. Both cannot be `None`.

        :param token_id: The ID of the token.
        :param name: The name of the token.
        :param expiration_days: The number of days in which the token would expire since it was last used.
            Valid values are 1-90. Default is 90.
        :return: None
        """

        if not name and not expiration_days:
            raise ValueError('name and/or expiration_days must be provided.')

        if not name and expiration_days:  # only updating expiration days which is a different API call
            data = {
                'tokenExpirationDays': expiration_days
            }
            return self.britive.patch(f'{self.base_url}/{token_id}', json=data)

        # updating the name and possibly the expiration days - if expiration days not provided make a call
        # to get the current expiration days and use that number.

        data = {
            'name': name,
            'tokenExpirationDays': expiration_days or self.get(token_id=token_id)['tokenExpirationDays']
        }
        return self.britive.put(f'{self.base_url}/{token_id}', json=data)




