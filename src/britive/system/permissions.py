
class SystemPermissions:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/policy-admin/permissions'

    @staticmethod
    def _validate_identifier_type(identifier_type):
        if identifier_type not in ['id', 'name']:
            raise ValueError(f'identifier_type of {identifier_type} is invalid. Only `name` and `id` are allowed.')

    def list(self, filter_expression: str = '') -> list:
        """
        List system level permissions.

        :param filter_expression: Filter based on `name`. Valid operators are `eq`, `sw`, and
            `co`. Example: name co view
        :returns: List of permissions.
        """

        params = {}
        if filter_expression:
            params['filter'] = filter_expression
        return self.britive.get(self.base_url, params=params)

    def get(self, permission_identifier: str, identifier_type: str = 'name') -> dict:
        """
        Get details of the specified permission.

        :param permission_identifier: The ID or name of the permission.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :returns: Details of the specified permission.
        """

        self._validate_identifier_type(identifier_type)

        return self.britive.get(f'{self.base_url}/{permission_identifier}')

    def create(self, permission: dict) -> dict:
        """
        Create a system level permission.

        :param permission: The permission to create. Use `permissions.build` to assist in constructing a proper
            permission document.
        :returns: Details of the newly created permission.
        """

        return self.britive.post(self.base_url, json=permission)
    
    def update(self, permission_identifier: str, permission: dict, identifier_type: str = 'name') -> None:
        """
        Update a system level permission.

        :param permission_identifier: The ID or name of the permission to update.
        :param permission: The permission to update. Use `permissions.build` to assist in constructing a proper
            permission document.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :returns: None.
        """

        self._validate_identifier_type(identifier_type)

        if permission.get('isInline'):
            raise ValueError('attribute isInline is set to True - cannot update an inline permission.')

        permission.pop('isInline', None)  # InvalidRequest: 400 - PA-0059 - isInline is not allowed to update
        permission.pop('isReadOnly', None)
        return self.britive.patch(f'{self.base_url}/{permission_identifier}', json=permission)

    def delete(self, permission_identifier: str, identifier_type: str = 'name') -> None:
        """
        Delete a system level permission.

        :param permission_identifier: The ID or name of the permission to delete.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :returns: None.
        """

        self._validate_identifier_type(identifier_type)
        return self.britive.delete(f'{self.base_url}/{permission_identifier}')

    @staticmethod
    def build(name: str, consumer: str, actions: list, resources: list = [], description: str = '',
              read_only: bool = False, is_inline: bool = False) -> dict:
        """
        Build a permission document given the provided inputs.

        :param name: The name of the permission.
        :param consumer: List of permission names or ids this permission grants.
        :param actions: List of action names for the permission.
        :param resources: List of resources IDs for which to scope this permission. If omitted then `*` will be applied.
        :param description: An optional description of the permission.
        :param read_only: Indicates if the permission is a read only. Defaults to `False`.
        :param is_inline: Indicates if the permission is inline to a role/policy. Defaults to `False`. `False`
            indicates that the permission is its own entity which can be assigned to roles/polices. `True` indicates
            the permissions is unique/inline to an role/policy.
        :return: A dict which can be provided as a permission document to `create` and `update`.
        """

        # put it all together
        permission = {
            'name': name,
            'description': description,
            'isReadOnly': read_only,
            'isInline': is_inline,
            'consumer': consumer,
            'actions': actions,
            'resources': resources if len(resources) > 0 else ['*']
        }

        return permission
