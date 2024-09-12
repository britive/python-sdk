
class SystemRoles:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/policy-admin/roles'

    @staticmethod
    def _validate_identifier_type(identifier_type):
        if identifier_type not in ['id', 'name']:
            raise ValueError(f'identifier_type of {identifier_type} is invalid. Only `name` and `id` are allowed.')

    def list(self, filter_expression: str = '') -> list:
        """
        List system level roles.

        :param filter_expression: Filter based on `name`. Valid operators are `eq`, `sw`, and
            `co`. Example: name co security
        :returns: List of roles.
        """

        params = {}
        if filter_expression:
            params['filter'] = filter_expression
        return self.britive.get(self.base_url, params=params)

    def get(self, role_identifier: str, identifier_type: str = 'name', verbose: bool = False) -> dict:
        """
        Get details of the specified role.

        :param role_identifier: The ID or name of the role.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :param verbose: Whether to return a more compact response (the default) or a more verbose response.
        :returns: Details of the specified role.
        """

        self._validate_identifier_type(identifier_type)
        params = {
            'compactResponse': not verbose
        }
        return self.britive.get(f'{self.base_url}/{role_identifier}', params=params)

    def create(self, role: dict) -> dict:
        """
        Create a system level role.

        :param role: The role to create. Use `roles.build` to assist in constructing a proper role document.
        :returns: Details of the newly created role.
        """

        return self.britive.post(self.base_url, json=role)
    
    def update(self, role_identifier: str, role: dict, identifier_type: str = 'name') -> None:
        """
        Update a system level role.

        :param role_identifier: The ID or name of the role to update.
        :param role: The role to update. Use `roles.build` to assist in constructing a proper role document.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :returns: None.
        """

        self._validate_identifier_type(identifier_type)
        return self.britive.patch(f'{self.base_url}/{role_identifier}', json=role)

    def delete(self, role_identifier: str, identifier_type: str = 'name') -> None:
        """
        Delete a system level role.

        :param role_identifier: The ID or name of the role to delete.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :returns: None.
        """

        self._validate_identifier_type(identifier_type)
        return self.britive.delete(f'{self.base_url}/{role_identifier}')

    @staticmethod
    def build(name: str, permissions: list, description: str = '', read_only: bool = False,
              identifier_type: str = 'name') -> dict:
        """
        Build a role document given the provided inputs.

        :param name: The name of the role.
        :param permissions: List of permission names or ids this role grants.
        :param description: An optional description of the role.
        :param read_only: Indicates if the role is a read only. Defaults to `False`.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers are being provided to `permissions`. Either all identifiers must be names or all
            identifiers must be IDs.
        :return: A dict which can be provided as a role document to `create` and `update`.
        """

        # put it all together
        role = {
            'name': name,
            'description': description,
            'isReadOnly': read_only,
            'permissions': [{identifier_type: p} for p in permissions]
        }

        return role
