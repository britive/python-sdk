from britive.exceptions import NotFound

from .identity_attributes import CustomAttributes

valid_statues = ['active', 'inactive']
identity_type_labels = {'ServiceIdentity': 'a service identity', 'AIIdentity': 'an AI identity'}


class ServiceIdentities:
    def __init__(self, britive, identity_type: str = 'ServiceIdentity') -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/users'
        self.custom_attributes = CustomAttributes(britive)
        self.identity_type = identity_type

    def list(self, filter_expression: str = None, include_tags: bool = False) -> list:
        """
        Provide an optionally filtered list of all service identities.

        :param filter_expression: filter list of users based on name, status, or role. The supported operators
             are 'eq' and 'co'. Example: 'name co "Smith"'
        :param include_tags: if this is set to true, tags/group memberships are returned.
        :return: List of service identity records
        """

        params = {'type': self.identity_type, 'page': 0, 'size': 100}
        if filter_expression:
            params['filter'] = filter_expression
        if include_tags:
            params['includeTags'] = 'true'

        return self.britive.get(self.base_url, params)

    def get(self, service_identity_id: str) -> dict:
        """
        Provide details of the given service_identity.

        :param service_identity_id: The ID  of the service identity.
        :return: Details of the specified service identity.
        :raises NotFound: if the ID does not exist or is not of this collection's identity type.
        """

        # the platform returns any identity type for this ID, so check it matches this collection
        service_identity = self.britive.get(f'{self.base_url}/{service_identity_id}')
        if service_identity.get('type') != self.identity_type:
            label = identity_type_labels.get(self.identity_type, self.identity_type)
            raise NotFound(f'{service_identity_id} is not {label}.')
        return service_identity

    def get_by_name(self, name: str) -> list:
        """
        Return service identities whose name field contains `name`.

        :param name: The name (or part of the name) of the service identity you wish to get
        :return: Details of the specified service identities. If no service identity is found will return an empty list.
        """

        return self.list(filter_expression=f'name co "{name}"')

    def get_by_status(self, status: str) -> list:
        """
        Return a list of service identities filtered to `status`.

        :param status: valid values are `active` and `inactive`
        :return:
        """

        if status not in valid_statues:
            raise ValueError(f'status {status} not allowed.')

        return self.list(filter_expression=f'status eq "{status}"')

    def search(self, search_string: str) -> list:
        """
        Search all user fields for the given `search_string` and returns
        a list of matched service identities.

        :param search_string:
        :return: List of user records
        """

        params = {'type': self.identity_type, 'page': 0, 'size': 100, 'searchText': search_string}

        return self.britive.get(self.base_url, params)

    def create(self, **kwargs) -> dict:
        """
        Create a new service identity.

        :param kwargs: Valid fields are...
            name - required
            description
            status - valid values are active, inactive - if omitted will default to active
        :return: Details of the newly created user.
        """

        required_fields = ['name']

        kwargs['type'] = self.identity_type
        if 'status' not in kwargs:
            kwargs['status'] = 'active'

        if kwargs['status'] not in valid_statues:
            raise ValueError(f'invalid status {kwargs["status"]}')

        if not all(x in kwargs for x in required_fields):
            raise ValueError('Not all required keyword arguments were provided.')

        return self.britive.post(self.base_url, json=kwargs)

    def update(self, service_identity_id: str, **kwargs) -> dict:
        """
        Update the specified attributes of the provided service identity.

        Acceptable attributes are `name` and `description`.

        :param service_identity_id: The ID of the service identity to update
        :param kwargs: The attributes to update for the service identity
        :return: A dict containing the newly updated service identity details
        """

        # get the existing identity first, which also confirms it is of this collection's identity type
        existing = self.get(service_identity_id)
        if 'name' not in kwargs:
            kwargs['name'] = existing['name']

        # add some required elements to the kwargs passed in by the caller
        kwargs['type'] = self.identity_type
        kwargs['roleName'] = ''

        self.britive.patch(f'{self.base_url}/{service_identity_id}', json=kwargs)

        # return the updated service identity record
        return self.get(service_identity_id)

    def delete(self, service_identity_id: str) -> None:
        """
        Delete a service identity.

        :param service_identity_id: The ID of the service identity to delete
        :return: None
        :raises NotFound: if the ID does not exist or is not of this collection's identity type.
        """

        self.get(service_identity_id)
        self.britive.delete(f'{self.base_url}/{service_identity_id}')

    def enable(self, service_identity_id: str = None, service_identity_ids: list = None) -> object:
        """
        Enable the given service identities.

        You can pass in both `service_identity_id` for a single user and `service_identity_ids` to enable multiple
        service identities in one call. If both `service_identity_id` and `service_identity_ids` are provided they
        will be merged together into one list.

        :param service_identity_id: The ID of the user you wish to enable.
        :param service_identity_ids: A list of user IDs that you wish to enable.
        :return: if `service_identity_ids` is set will return a list of user records, else returns a user dict
        :raises ValueError: if neither `service_identity_id` nor `service_identity_ids` is provided.
        :raises NotFound: if any ID does not exist or is not of this collection's identity type; no identity is changed.
        """

        return self.__set_status(
            'enabled', service_identity_id=service_identity_id, service_identity_ids=service_identity_ids
        )

    def disable(self, service_identity_id: str = None, service_identity_ids: list = None) -> object:
        """
        Disable the given service identities.

        You can pass in both `service_identity_id` for a single service identity and `service_identity_ids` to disable
        multiple service identitie at in one call. If both `service_identity_id` and `service_identity_ids` are
        provided they will be merged together into one list.

        :param service_identity_id: The ID of the user you wish to disable.
        :param service_identity_ids: A list of user IDs that you wish to disable.
        :return: if `user_ids` is set will return a list of user records, else returns a user dict
        :raises ValueError: if neither `service_identity_id` nor `service_identity_ids` is provided.
        :raises NotFound: if any ID does not exist or is not of this collection's identity type; no identity is changed.
        """

        return self.__set_status(
            'disabled', service_identity_id=service_identity_id, service_identity_ids=service_identity_ids
        )

    def __set_status(self, status: str, service_identity_id: str = None, service_identity_ids: list = None) -> object:
        computed_identities = list(service_identity_ids or [])
        if service_identity_id:
            computed_identities.append(service_identity_id)

        # de-dup, preserving order
        computed_identities = list(dict.fromkeys(computed_identities))
        if not computed_identities:
            raise ValueError('service_identity_id or service_identity_ids is required.')

        # the statuses endpoints accept any identity type and skip unknown ids, so check every id first
        for computed_identity in computed_identities:
            self.get(computed_identity)

        response = self.britive.post(f'{self.base_url}/{status}-statuses', json=computed_identities)
        if service_identity_ids:
            return response
        if not response:
            raise NotFound(f'{service_identity_id} was not {status}.')
        return response[0]


class ServiceIdentityTokens:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}'

    def __validate_token_expiration(self, days) -> None:
        if not (1 <= days <= 90):
            raise ValueError('invalid token expiration value - must ust be between 1 and 90')

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

        self.__validate_token_expiration(token_expiration_days)

        data = {'tokenExpirationDays': token_expiration_days}

        return self.britive.post(f'{self.base_url}/users/{service_identity_id}/tokens', json=data)

    def update(self, service_identity_id: str, token_expiration_days: int = 90) -> None:
        """
        Update the token expiration days for an existing service identity token.

        :param service_identity_id: The ID of the service identity.
        :param token_expiration_days: The number of days in which token would expire since it was last used.
            The token expiration days can be any value between 1 day and 90 days.
        :return: None
        """

        self.__validate_token_expiration(token_expiration_days)

        data = {'tokenExpirationDays': token_expiration_days}

        return self.britive.post(f'{self.base_url}/users/{service_identity_id}/tokens', json=data)

    def get(self, service_identity_id: str) -> dict:
        """
        Return details of the token associated with the service identity. Only one token can exist per service identity.

        :param service_identity_id: The ID of the service identity.
        :return: Details of the service identity token
        """

        return self.britive.get(f'{self.base_url}/users/{service_identity_id}/tokens')
