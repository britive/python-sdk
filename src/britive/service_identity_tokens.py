def validate_token_expiration(days):
    if not (1 <= days <= 90):
        raise ValueError(f'invalid token expiration value - must ust be between 1 and 90')


class ServiceIdentityTokens:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}'

    def create(self, service_identity_id: str, token_expiration_days: int = 90) -> dict:
        """
        Create a token for a given service identity.

        The token has the same privileges assigned to the service identity. When this token is created, the old token
        associated with the identity provider will be removed. A service identity can have only one token at any given
        time. The token that is generated will be returned only once.

        :param service_identity_id: The ID of the service identity.
        :param token_expiration_days: The number of days in which token would expire since it was last used.
            The token expiration days can be any value between 1 day and 90 days.
        :return:
        """

        validate_token_expiration(token_expiration_days)

        data = {
            'tokenExpirationDays': token_expiration_days
        }

        return self.britive.post(f'{self.base_url}/users/{service_identity_id}/tokens', json=data)

    def update(self, service_identity_id: str, token_expiration_days: int = 90) -> None:
        """
        Update the token expiration days for an existing service identity token.

        :param service_identity_id: The ID of the service identity.
        :param token_expiration_days: The number of days in which token would expire since it was last used.
            The token expiration days can be any value between 1 day and 90 days.
        :return: None
        """

        validate_token_expiration(token_expiration_days)

        data = {
            'tokenExpirationDays': token_expiration_days
        }

        self.britive.patch(f'{self.base_url}/users/{service_identity_id}/tokens', json=data)
        return self.get(service_identity_id)

    def get(self, service_identity_id: str) -> dict:
        """
        Return details of the token associated with the service identity. Only one token can exist per service identity.

        :param service_identity_id: The ID of the service identity.
        :return: Details of the service identity token
        """

        return self.britive.get(f'{self.base_url}/users/{service_identity_id}/tokens')

