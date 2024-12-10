class ManagedPermissions:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def create(
        self,
        application_id: str,
        name: str,
        permissions: list,
        description: str = '',
        type: str = 'role',
        tags: list = None,
    ) -> dict:
        """
        Create a new managed permission for use with the specified application.

        :param application_id: The ID of the application.
        :param name: The name of the new managed permission.
        :param permissions: The policies of the new managed permission.
        :param description: The description of the new managed permission.
        :param type: The type of the new managed permission.
        :param tags: The tags of the new managed permission.
        :return: Dict containing details of the new managed permission.
        """

        data = {
            'childPermissions': permissions,
            'description': description,
            'name': name,
            'tags': [] if tags is None else tags,
            'type': type,
        }

        return self.britive.get(f'{self.base_url}/{application_id}/britive-managed/permissions', json=data)

    def list(self, application_id: str, search_text: str = None) -> list:
        """
        Return the details of all managed permissions associated the specific application.

        :param application_id: The ID of the application.
        :param search_text: Filter based on string match.
        :return: List containing details of each managed permission.
        """

        params = {} if search_text is None else {'searchText': search_text}

        return self.britive.get(f'{self.base_url}/{application_id}/britive-managed/permissions', params=params)

    def get(self, application_id: str, permission_id: str) -> dict:
        """
        Return details of the managed permission.

        :param application_id: The ID of the application.
        :param permission_id: The ID of the managed permission.
        :return: Dict containing details of the managed permission.
        """

        return self.britive.get(f'{self.base_url}/{application_id}/britive-managed/permissions/{permission_id}')

    def validate_policy(self, application_id: str, policy: dict) -> dict:
        """
        Validate the provided permission policy.

        :param application_id:
        :param policy: The policy, in JSON format, to validate.
        :return: Dict of findings.
        """

        return self.britive.post(f'{self.base_url}/{application_id}/britive-managed/permissions/validate', json=policy)

    def delete(self, application_id: str, permission_id: str) -> None:
        """
        Delete the managed permission.

        :param application_id: The ID of the application.
        :param permission_id: The ID of the managed permission.
        :return: None.
        """

        return self.britive.delete(f'{self.base_url}/{application_id}/britive-managed/permissions/{permission_id}')
