from .labels import Labels
from .permissions import Permissions
from .types import Types


class Resources:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/resources'
        self.labels = Labels(britive)
        self.permissions = Permissions(britive)
        self.types = Types(britive)

    def create(self, name: str, resource_type_id: str, description: str = '', param_values: dict = None) -> dict:
        """
        Create a new resource.

        :param name: Name of the resource.
        :param description: Description of the resource.
        :param resource_type_id: ID of the resource type.
        :param param_values: Dict of param values.
        :return: Created resource.
        """

        if param_values is None:
            param_values = {}

        params = {
            'name': name,
            'description': description,
            'resourceType': {'id': resource_type_id},
            'paramValues': param_values,
        }

        return self.britive.post(self.base_url, json=params)

    def add_broker_pools(self, resource_id: str, pools: list) -> list:
        """
        Add broker pools to a resource.

        :param resource_id: ID of the resource.
        :param pools: List of broker pools.
        :return: List of broker pools.
        """

        return self.britive.post(f'{self.base_url}/{resource_id}/broker-pools', json=pools)

    def get(self, resource_id: str) -> dict:
        """
        Retrieve a resource by ID.

        :param resource_id: ID of the resource.
        :return: Resource.
        """

        return self.britive.get(f'{self.base_url}/{resource_id}')

    def list(self, filter_expression: str = None, search_text: str = None) -> list:
        """
        Retrieve all resources.

        :param filter_expression: Parameter to filter resources by name. Example: `name eq profile1`.
        :param search_text: Filter resources by search text.
        :return: List of resources.
        """

        params = {
            **({'filter': filter_expression} if filter_expression else {}),
            **({'searchText': search_text} if search_text else {}),
        }

        return self.britive.get(f'{self.base_url}', params=params)

    def update(self, resource_id: str, description: str = None, resource_labels: list = None) -> dict:
        """
        Update a resource.

        :param resource_id: ID of the resource.
        :param name: Name of the resource.
        :param description: Description of the resource.
        :param resource_labels: List of Resource Labels.
        :return: Updated resource.
        """

        params = {
            'name': self.get(resource_id)['name'],
            'resourceType': {'id': self.get(resource_id)['resourceType']['id']},
            **({'description': description} if description else {}),
            **({'resourceLabels': resource_labels} if resource_labels else {}),
        }

        return self.britive.put(f'{self.base_url}/{resource_id}', json=params)

    def delete(self, resource_id: str) -> None:
        """
        Delete a resource.

        :param resource_id: ID of the resource.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{resource_id}')
