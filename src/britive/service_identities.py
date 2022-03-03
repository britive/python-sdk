valid_statues = ['active', 'inactive']


class ServiceIdentities:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/users'

    def list(self, filter_expression: str = None) -> list:
        """
        Provide an optionally filtered list of all service identities.

        :param filter_expression: filter list of users based on name, status, or role. The supported operators
             are 'eq' and 'co'. Example: 'name co "Smith"'
        :return: List of service identity records
        """

        params = {
            'type': 'ServiceIdentity',
            'page': 0,
            'size': 100
        }
        if filter_expression:
            params['filter'] = filter_expression

        return self.britive.get(self.base_url, params)

    def get(self, service_identity_id: str) -> dict:
        """
        Provide details of the given service_identity.

        :param service_identity_id: The ID  of the service identity.
        :return: Details of the specified user.
        """

        params = {
            'type': 'ServiceIdentity'
        }
        return self.britive.get(f'{self.base_url}/{service_identity_id}', params=params)

    def get_by_name(self, name: str) -> list:
        """
        Return service identities whose name field contains `name`.

        :param name: The name (or part of the name) of the service identity you wish to get
        :return: Details of the specified service identities. If no service identity is found will return an empty list.
        """

        service_identities = self.list(filter_expression=f'name co "{name}"')
        return service_identities

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

        params = {
            'type': 'ServiceIdentity',
            'page': 0,
            'size': 100,
            'searchText': search_string
        }

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

        kwargs['type'] = 'ServiceIdentity'
        if 'status' not in kwargs.keys():
            kwargs['status'] = 'active'

        if kwargs['status'] not in valid_statues:
            raise ValueError(f'invalid status {kwargs["status"]}')

        if not all(x in kwargs.keys() for x in required_fields):
            raise ValueError('Not all required keyword arguments were provided.')

        response = self.britive.post(self.base_url, json=kwargs)
        return response

    # TODO - check this once a bug fix has been deployed
    def update(self, service_identity_id: str, **kwargs) -> dict:
        """
        Update the specified attributes of the provided service identity.

        Acceptable attributes are `name` and `description`.

        :param service_identity_id: The ID of the service identity to update
        :param kwargs: The attributes to update for the service identity
        :return: A dict containing the newly updated service identity details
        """

        if 'name' not in kwargs.keys():
            existing = self.get(service_identity_id)
            kwargs['name'] = existing['name']

        # add some required elements to the kwargs passed in by the caller
        kwargs['type'] = 'ServiceIdentity'
        kwargs['roleName'] = ''

        self.britive.patch(f'{self.base_url}/{service_identity_id}', json=kwargs)

        # return the updated service identity record
        return self.get(service_identity_id)

    def delete(self, service_identity_id: str) -> None:
        """
        Delete a service identity.

        :param service_identity_id: The ID of the service identity to delete
        :return: None
        """

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
        """

        computed_identities = []
        if service_identity_ids:
            computed_identities += service_identity_ids
        if service_identity_id:
            computed_identities.append(service_identity_id)

        # de-dup
        computed_identities = list(set(computed_identities))
        response = self.britive.post(f'{self.base_url}/enabled-statuses', json=computed_identities)
        if not service_identity_ids:
            return response[0]
        return response

    def disable(self, service_identity_id: str = None, service_identity_ids: list = None) -> object:
        """
        Disable the given service identities.

        You can pass in both `service_identity_id` for a single service identity and `service_identity_ids` to disable
        multiple service identitie at in one call. If both `service_identity_id` and `service_identity_ids` are
        provided they will be merged together into one list.

        :param service_identity_id: The ID of the user you wish to disable.
        :param service_identity_ids: A list of user IDs that you wish to disable.
        :return: if `user_ids` is set will return a list of user records, else returns a user dict
        """

        computed_identities = []
        if service_identity_ids:
            computed_identities += service_identity_ids
        if service_identity_id:
            computed_identities.append(service_identity_id)

        # de-dup
        computed_identities = list(set(computed_identities))
        response = self.britive.post(f'{self.base_url}/disabled-statuses', json=computed_identities)
        if not service_identity_ids:
            return response[0]
        return response
