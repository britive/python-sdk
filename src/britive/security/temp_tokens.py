class TempTokens:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/tokens/temp'

    def create(self, duration_seconds: int = None) -> dict:
        """
        Create a temporary bearer token for the caller's identity.

        Requires the securityadmin.temptoken.create permission. Requests made with the token use the caller's
        permissions at the time of each request. A temporary token cannot be used to create another temporary token.

        :param duration_seconds: Requested lifetime in seconds. Must be a positive integer within the tenant's
            configured maximum and the 86400-second platform limit. If omitted, the API uses the tenant's configured
            lifetime, bounded by the platform limit. The API validates the duration and rejects requests above the
            effective maximum. Expiration enforcement can lag by about a minute.
        :return: Response dictionary containing accessToken and expiresOn, an expiration date-time string.
            The token is returned once and cannot be retrieved afterwards.
        """

        data = {}
        if duration_seconds is not None:
            data['durationSeconds'] = duration_seconds

        return self.britive.post(self.base_url, json=data)

    def list(self) -> list:
        """
        Placeholder for listing temporary tokens. Makes no HTTP request.

        :raises NotImplementedError: This SDK operation awaits the API contract.
        """

        raise NotImplementedError('Listing temporary tokens is not implemented in the SDK; awaiting the API contract.')

    def get(self, token_id: str) -> dict:
        """
        Placeholder for viewing a temporary token. Makes no HTTP request.

        :param token_id: Provisional token identifier, subject to the future API contract.
        :raises NotImplementedError: This SDK operation awaits the API contract.
        """

        raise NotImplementedError('Viewing temporary tokens is not implemented in the SDK; awaiting the API contract.')

    def revoke(self, token_id: str) -> None:
        """
        Placeholder for revoking a temporary token. Makes no HTTP request.

        :param token_id: Provisional token identifier, subject to the future API contract.
        :raises NotImplementedError: This SDK operation awaits the API contract.
        """

        raise NotImplementedError('Revoking temporary tokens is not implemented in the SDK; awaiting the API contract.')
