class Types:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/resource-types'

    def create(self, name: str, description: str = '', fields: list = None) -> dict:
        """
        Create a new resource type.

        :param name: Name of the resource type.
        :param description: Description of the resource type.
        :param fields: List of Resource Type fields.
            Example: [
                {
                    'name': 'string',
                    'paramType': 'string'|'multiline'|'password',
                    'isMandatory': True|False
                },
                ...
            ]
        :return: Created resource type.
        """
        params = {
            'name': name,
            'description': description,
        }

        if fields:
            params['parameters'] = fields

        return self.britive.post(self.base_url, json=params)

    def get(self, resource_type_id: str) -> dict:
        """
        Retrieve a resource type by ID.

        :param resource_type_id: ID of the resource type.
        :return: Resource type.
        """
        return self.britive.get(f'{self.base_url}/{resource_type_id}')

    def list(self) -> list:
        """
        Retrieve all resource types.

        :return: List of resource types.
        """

        return self.britive.get(self.base_url)['data']

    def update(self, resource_type_id: str, description: str = None, fields: list = None) -> dict:
        """
        Update a resource type.

        :param resource_type_id: ID of the resource type.
        :param description: Description of the resource type.
        :param fields: List of Resource Type fields.
            Example: [
                {
                    'name': 'string',
                    'paramType': 'string'|'multiline'|'password',
                    'isMandatory': True|False
                },
                ...
            ]
        :return: Updated resource type.
        """
        params = {}

        if description:
            params['description'] = description
        if fields:
            params['parameters'] = fields

        return self.britive.put(f'{self.base_url}/{resource_type_id}', json=params)

    def delete(self, resource_type_id: str) -> None:
        """
        Delete a resource type.

        :param resource_type_id: ID of the resource type.
        :return: None
        """
        return self.britive.delete(f'{self.base_url}/{resource_type_id}')
