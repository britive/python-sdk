class ResourcePermissions:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager'

    def list(self, resource_type_id) -> list:
        """
        Retrieve all permissions for a resource type.

        :param resource_type_id: ID of the resource type.
        :return: List of permissions.
        """

        return self.britive.get(f'{self.base_url}/resource-types/{resource_type_id}/permissions')

    def create(self, resource_type_id, **kwargs) -> dict:
        """
        Create a new permission for a resource type.

        :param resource_type_id: ID of the resource type.
        :param kwargs: Valid fields are...
            name
            description
            createdBy
            updatedBy
            version
            checkinURL 
            checkoutURL
            checkinFileName
            checkoutFileName
            checkinTimeLimit
            checkoutTimeLimit
            variables - List of variables
        :return: Created permission.
        """

        params = {
            'resourceTypeId' : resource_type_id,
            'isDraft' : False,
        }

        return self.britive.post(f'{self.base_url}/permissions', json=params)