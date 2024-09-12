class ProfileManager:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/profiles'
    def create(self, name, description, expiration_duration):
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
        return self.britive.put(f'{self.base_url}/{profile_id}', json=params)
    
    def clone(self, profile_id, options = [], ignore_errors = False):
        """
        Clone a profile.
        :param profile_id: ID of the profile.
        :param options: List of options.
        :param ignore_errors: Ignore errors.
        :return: Cloned profile.
        """
        return self.britive.post(f'{self.base_url}/{profile_id}/clone?otions={options}&ignoreErrors={ignore_errors}')
    
    def delete(self, profile_id):
        """
        Delete a profile.
        :param profile_id: ID of the profile.
        :return: None
        """
        return self.britive.delete(f'{self.base_url}/{profile_id}')
    
    def add_association(self, profile_id, associations=[]):
        """
        Add associations to a resource profile.
        :param profile_id: ID of the profile.
        :param associations: List of associations.
        :return: Updated profile.
        """
        associations_dict = {}
        for i in range(len(associations)):
            associations_dict[f'additionalProp{i}'] = associations[i]
        params = {
            'associations': associations_dict
        }
        return self.britive.post(f'{self.base_url}/{profile_id}/associations', json=params)
    
    def list_associations(self, profile_id):
        """
        Retrieve all associations for a resource profile.
        :param profile_id: ID of the profile.
        :return: List of associations.
        """
        return self.britive.get(f'{self.base_url}/{profile_id}/associations')
    
    def add_permissions(self, profile_id, permission_id, version, resource_type_id, variables=[]):
        """
        Add permissions to a resource profile.
        :param profile_id: ID of the profile.
        :param permission_id: ID of the permission.
        :param version: Version of the permission.
        :param resource_type_id: ID of the resource type.
        :param variables: List of variables.
        :return: Updated profile.
        """
        params = {
            'permissionId': permission_id,
            'version': version,
            'resourceTypeId': resource_type_id,
            'variables': variables
        }
        return self.britive.post(f'{self.base_url}/{profile_id}/permissions', json=params)

    def list_permissions(self, profile_id):
        """
        Retrieve all permissions for a resource profile.
        :param profile_id: ID of the profile.
        :return: List of permissions.
        """
        return self.britive.get(f'{self.base_url}/{profile_id}/permissions')
    
    def list_available_permissions(self, profile_id):
        """
        Used to retrieve permissions available to the resource profile.
        :param profile_id: ID of the profile.
        :return: List of permissions.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}/available-permissions')
    
    def update_permission_variables(self, profile_id, permission_id, variables=[]):
        """
        Update permission variables for a resource profile.
        :param profile_id: ID of the profile.
        :param permission_id: ID of the permission.
        :param variables: List of variables.
        :return: Updated profile.
        """
        params = {
            'variables': variables
        }
        return self.britive.put(f'{self.base_url}/{profile_id}/permissions/{permission_id}', json=params)
    
    def delete_permission(self, profile_id, permission_id):
        """
        Delete a permission from a resource profile.
        :param profile_id: ID of the profile.
        :param permission_id: ID of the permission.
        :return: None
        """
        return self.britive.delete(f'{self.base_url}/{profile_id}/permissions/{permission_id}')
    
    def get_system_values(self, resource_type_id):
        """
        Retrieve system values for a resource type.
        :param resource_type_id: ID of the resource type.
        :return: System values.
        """
        return self.britive.get(f'{self.base_url}/permissions/system-defined-values', params={'resourceTypeId': resource_type_id})
    
