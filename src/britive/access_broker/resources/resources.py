from .labels import Labels
from .types import Types
from .permissions import Permissions
class Resources:
    def __init__(self, britive):
        self.britive = britive
        self.labels = Labels(britive)
        self.types = Types(britive)
        self.permissions = Permissions(britive)
    def get_system_values(self, resource_type_id):
        """
        Retrieve system values for a resource type.
        :param resource_type_id: ID of the resource type.
        :return: System values.
        """
        return self.britive.get(f'{self.base_url}/permissions/system-defined-values', params={'resourceTypeId': resource_type_id})
    
