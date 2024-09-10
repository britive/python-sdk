from .labels import Labels
from .types import Types
from .permissions import Permissions
class Resources:
    def __init__(self, britive):
        self.britive = britive
        self.labels = Labels(britive)
        self.types = Types(britive)
        self.permissions = Permissions(britive)
        self.base_url = f'{self.britive.base_url}/resource-manager/resources'
    def list(self):
        """
        Retrieve all resources.

        :return: List of resources.
        """
        return self.britive.get(f'{self.base_url}', params={})
    def get(self, resource_id) -> dict:
        """
        Retrieve a resource by ID.

        :param resource_id: ID of the resource.
        :return: Resource.
        """
        return self.britive.get(f'{self.base_url}/{resource_id}')
    def create(self, name, resource_type_id, description='') -> dict:
        """
        Create a new resource.

        :param name: Name of the resource.
        :param description: Description of the resource.
        :param resource_type_id: ID of the resource type.
        :return: Created resource.
        """
        params = {
            'name': name,
            'description': description,
            'resourceType': {'id': resource_type_id},
        }
        return self.britive.post(self.base_url, json=params)

    def update(self, resource_id, description, resource_labels) -> dict:
        """
        Update a resource.

        :param resource_id: ID of the resource.
        :param name: Name of the resource.
        :param description: Description of the resource.
        :param resource_labels: Resource labels. Dict in form of {Resource-Type: [type], [Label Key] : [Label Value]}
        :return: Updated resource.
        """
        params = {
            'name': self.get(resource_id)['name'],
            'description': description,
            'resourceLabels': resource_labels,
            'resourceType': {'id': self.get(resource_id)['resourceType']['id']},
        }

        return self.britive.put(f'{self.base_url}/{resource_id}', json=params)
    def delete(self, resource_id) -> dict:
        """
        Delete a resource.
        :param resource_id: ID of the resource.
        :return: None
        """
        return self.britive.delete(f'{self.base_url}/{resource_id}')
    
    def add_broker_pools(self, pools : list, resource_id):
        """
        Add broker pools to a resource.
        :param pools: List of broker pools.
        :param resource_id: ID of the resource.
        :return: List of broker pools.
        """
        return self.britive.post(f'{self.base_url}/{resource_id}/broker-pools', json=pools)