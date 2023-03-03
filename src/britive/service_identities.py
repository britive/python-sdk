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

    def get_custom_identity_attributes(self, service_identity_id: str, as_dict: bool = False) -> any:
        """
        Retrieve the current custom attributes associated with the specified Service Identity.

        :param service_identity_id: The ID of the Service Identity.
        :param as_dict: Whether to return a key/value mapping vs the raw response which is a list.
        """
        response = self.britive.get(f'{self.base_url}/{service_identity_id}/custom-attributes')
        if as_dict:
            attrs = {}
            for attribute in response:
                if attribute in attrs.keys():  # need to handle the multi-value attributes
                    is_list = isinstance(attrs[attribute['attributeId']], list)

                    if not is_list:  # make it a list
                        attrs[attribute['attributeId']] = [attrs[attribute['attributeId']]]
                    attrs[attribute['attributeId']].appen(attribute['attributeValue'])
                else:
                    attrs[attribute['attributeId']] = attribute['attributeValue']
            return attrs
        else:
            return response

    def set_custom_identity_attributes(self, service_identity_id: str, custom_attributes_ids: dict = None,
                                       custom_attributes_names: dict = None) -> None:
        """
        Sets custom attributes for the provided Service Identity.

        :param service_identity_id: The IDs of the Service Identity.
        :param custom_attributes_ids: An attribute map where keys are the custom attribute ids and values are
            custom attribute values as strings or list of strings for multivalued attributes. This will be merged
            with `custom_attributes_names` and if there are duplicates this will win.
        :param custom_attributes_names: An attribute map where keys are the custom attribute names and values are
            custom attribute values as strings or list of strings for multivalued attributes. The names will be
            auto-converted to ids and merged with `custom_attributes_ids`. If there are duplicates
            `custom_attributes_ids` will win.
        """
        return self._modify_custom_identity_attributes(
            service_identity_id=service_identity_id,
            operation='add',
            custom_attributes_ids=custom_attributes_ids,
            custom_attributes_names=custom_attributes_names
        )

    def remove_custom_identity_attributes(self, service_identity_id: str, custom_attributes_ids: dict = None,
                                          custom_attributes_names: dict = None) -> None:
        """
        Removes custom attributes for the provided Service Identity.

        :param service_identity_id: The IDs of the Service Identity.
        :param custom_attributes_ids: An attribute map where keys are the custom attribute ids and values are
            custom attribute values as strings or list of strings for multivalued attributes. This will be merged
            with `custom_attributes_names` and if there are duplicates this will win.
        :param custom_attributes_names: An attribute map where keys are the custom attribute names and values are
            custom attribute values as strings or list of strings for multivalued attributes. The names will be
            auto-converted to ids and merged with `custom_attributes_ids`. If there are duplicates
            `custom_attributes_ids` will win.
        """
        return self._modify_custom_identity_attributes(
            service_identity_id=service_identity_id,
            operation='remove',
            custom_attributes_ids=custom_attributes_ids,
            custom_attributes_names=custom_attributes_names
        )

    def _modify_custom_identity_attributes(self, service_identity_id: str, operation: str,
                                           custom_attributes_ids: dict = None,
                                           custom_attributes_names: dict = None) -> None:
        if not custom_attributes_ids:
            custom_attributes_ids = {}

        if operation not in ['add', 'remove']:
            raise ValueError('operation must either be add or remove')

        # pull ids given names and merge into the ids dict if the ids dict doesn't already have the key
        if custom_attributes_names:
            existing_attributes = self.britive.identity_attributes.list()
            for name, value in custom_attributes_names.items():
                attribute_id = None
                for attr in existing_attributes:
                    if attr['name'] == name:
                        attribute_id = attr['id']
                        break
                if not attribute_id:
                    raise ValueError(f'custom identity attribute name value of {name} not found.')
                if attribute_id not in custom_attributes_ids.keys():
                    custom_attributes_ids[attribute_id] = value

        if len(custom_attributes_ids.keys()) == 0:
            raise ValueError('either custom_attributes_ids or custom_attributes_ids or both must be provided.')

        # now form the required payload
        attribute_list = []
        for attr_id, value in custom_attributes_ids.items():
            value = value if isinstance(value, list) else [value]  # handle multivalued attributes
            for v in value:
                attribute_list.append(
                    {
                        'op': operation,
                        'customUserAttribute': {
                            'attributeValue': v,
                            'attributeId': attr_id
                        }
                    }
                )

        return self.britive.patch(f'{self.base_url}/{service_identity_id}/custom-attributes', json=attribute_list)
