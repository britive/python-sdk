from .policies import Policies
from .permissions import Permissions

class Profile:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/profiles'
        self.policies = Policies(britive)
        self.permissions = Permissions(britive)
    def create(self, name, description="", expiration_duration=900000):
        """
        Create a new profile.
        :param name: Name of the profile.
        :param description: Description of the profile.
        :param expiration_duration: Expiration duration of the profile.
        :return: Created profile.
        """
        params = {
            'name': name,
            'description': description,
            'expirationDuration': expiration_duration
        }
        return self.britive.post(f'{self.base_url}', json=params)

    def list(self):
        """
        Retrieve all profiles.
        :return: List of profiles.
        """
        return self.britive.get(self.base_url, params={})
    
    def get(self, profile_id):
        """
        Retrieve a profile by ID.
        :param profile_id: ID of the profile.
        :return: Profile.
        """
        return self.britive.get(f'{self.base_url}/{profile_id}')
    
    def update(self, profile_id, name=None, description=None, expiration_duration=None):
        """
        Update a profile.
        :param profile_id: ID of the profile.
        :param name: Name of the profile.
        :param description: Description of the profile.
        :param expiration_duration: Expiration duration of the profile.
        :return: Updated profile.
        """
        params = {}
        if name:
            params['name'] = name
        if description:
            params['description'] = description
        if expiration_duration:
            params['expirationDuration'] = expiration_duration
        return self.britive.patch(f'{self.base_url}/{profile_id}', json=params)
    
    def delete(self, profile_id):
        """
        Delete a profile.
        :param profile_id: ID of the profile.
        :return: None
        """
        return self.britive.delete(f'{self.base_url}/{profile_id}')
    
    def add_association(self, profile_id, associations={}):
        """
        Add associations to a resource profile.
        :param profile_id: ID of the profile.
        :param associations: List of associations.
        :return: Updated profile.
        """
        params = {
            'associations': associations
        }
        return self.britive.post(f'{self.base_url}/{profile_id}/associations', json=params)
    
    def list_associations(self, profile_id):
        """
        Retrieve all associations for a resource profile.
        :param profile_id: ID of the profile.
        :return: List of associations.
        """
        return self.britive.get(f'{self.base_url}/{profile_id}/associations')
    def get_system_values(self, resource_type_id):
        """
        Retrieve system values for a resource type.
        :param resource_type_id: ID of the resource type.
        :return: System values.
        """
        return self.britive.get(f'{self.base_url}/permissions/system-defined-values', params={'resourceTypeId': resource_type_id})
    
