import requests


class Permissions:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager'

    def create(
        self,
        resource_type_id: str,
        name: str,
        description: str = '',
        checkin_file: bytes = None,
        checkout_file: bytes = None,
        variables: list = None,
    ) -> dict:
        """
        Create a new permission.

        :param resource_type_id: ID of the resource type.
        :param name: Name of the permission.
        :param description: Description of the permission.
        :param checkin_file: Checkin file.
        :param checkout_file: Checkout file.
        :param variables: List of variables.
        :return: Created permission.
        """

        if variables is None:
            variables = []

        create_params = {
            'description': description,
            'isDraft': True,
            'name': name,
            'resourceTypeId': resource_type_id,
        }
        permission = self.britive.post(f'{self.base_url}/permissions', json=create_params)

        if checkin_file and checkout_file:
            permissionId = permission['permissionId']
            urls = self.get_urls(permissionId)
            requests.put(urls['checkinURL'], files={'file': checkin_file})
            requests.put(urls['checkoutURL'], files={'file': checkout_file})
            update_params = {
                'checkinFileName': permissionId + '_checkin',
                'checkinTimeLimit': 60,
                'checkoutFileName': permissionId + '_checkout',
                'checkoutTimeLimit': 60,
                'description': description,
                'inlineFileExists': True,
                'isDraft': False,
                'name': name,
                'resourceTypeId': resource_type_id,
                'variables': variables,
            }
            permission = self.britive.put(f'{self.base_url}/permissions/{permissionId}', json=update_params)
            permission['permissionId'] = permissionId

        return permission

    def get(self, permission_id: str, version_id: str = None) -> dict:
        """
        Retrieve a permission by ID.

        :param permission_id: ID of the permission.
        :param version_id: ID of the version. Optional.
        :return: Permission.
        """

        if version_id:
            return self.britive.get(f'{self.base_url}/permissions/{permission_id}/{version_id}')

        return self.britive.get(f'{self.base_url}/permissions/{permission_id}')

    def get_system_values(self, resource_type_id: str):
        return self.britive.get(
            f'{self.base_url}/permissions/system-defined-values', params={'resourceTypeId': resource_type_id}
        )

    def get_urls(self, permission_id: str) -> dict:
        """
        Retrieve URLs for a permission.

        :param permission_id: ID of the permission.
        :return: URLs.
        """

        return self.britive.get(f'{self.base_url}/permissions/get-urls/{permission_id}')

    def list(self, resource_type_id: str, search_text: str = None) -> list:
        """
        Retrieve all permissions for a resource type.

        :param resource_type_id: ID of the resource type.
        :param search_text: filter resource types by search text.
        :return: List of permissions.
        """

        params = {**({'searchText': search_text} if search_text else {})}

        return self.britive.get(f'{self.base_url}/resource-types/{resource_type_id}/permissions', params=params)

    def update(
        self,
        permission_id: str,
        resource_type_id: str,
        name: str,
        checkin_file: bytes = None,
        checkin_time_limit: int = 60,
        checkout_file: bytes = None,
        checkout_time_limit: int = 60,
        **kwargs,
    ) -> dict:
        """
        Update a permission.

        :param permission_id: ID of the permission.
        :param resource_type_id: ID of the resource type.
        :param name: Name of the permission.
        :param checkin_file: File to upload for checkin.
        :param checkout_file: File to upload for checkout.
        :param kwargs: Valid fields are...
            checkinURL
            checkoutURL
            description
            variables - List of variables
            version
        :return: Updated permission.
        """

        valid_fields = [
            'checkinTimeLimit',
            'checkinURL',
            'checkoutTimeLimit',
            'checkoutURL',
            'description',
            'variables',
            'version',
        ]

        params = {k: v for k, v in kwargs.items() if k in valid_fields}
        params.update(
            name=name,
            permissionId=permission_id,
            resourceTypeId=resource_type_id,
            checkinTimeLimit=checkin_time_limit,
            checkoutTimeLimit=checkout_time_limit,
        )

        if checkin_file and checkout_file:
            urls = self.get_urls(permission_id)
            requests.put(urls['checkinURL'], files={'file': checkin_file})
            requests.put(urls['checkoutURL'], files={'file': checkout_file})
            params.update(
                checkinFileName=permission_id + '_checkin',
                checkinURL=urls['checkinURL'],
                checkoutFileName=permission_id + '_checkout',
                checkoutURL=urls['checkoutURL'],
                inlineFileExists=True,
            )

        return self.britive.put(f'{self.base_url}/permissions/{permission_id}', json=params)

    def delete(self, permission_id: str, version_id: str = None) -> None:
        """
        Delete a permission.

        :param permission_id: ID of the permission.
        :param version_id: Version of the permission. Optional.
        :return: None
        """

        if version_id:
            return self.britive.delete(f'{self.base_url}/permissions/{permission_id}/{version_id}')
        return self.britive.delete(f'{self.base_url}/permissions/{permission_id}')
