import random
import requests
class Permissions:
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
    
    def update(self, permission_id, file : bytes = None, **kwargs) -> dict:     
        """
        Update a permission.
        :param permission_id: ID of the permission.
        :param file: File to upload.
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
        :return: Updated permission.
        """
        if file:
            urls = self.get_urls(permission_id)
            requests.put(urls['checkinURL'], files={'file': file})
            kwargs['checkinFileName'] = permission_id + '_checkin'
            kwargs['checkoutFileName'] = permission_id + '_checkout'
            kwargs['inlineFileExists'] = True
            kwargs['checkinURL'] = urls['checkinURL']
            kwargs['checkoutURL'] = urls['checkoutURL']
        return self.britive.put(f'{self.base_url}/permissions/{permission_id}', json=kwargs)
        
    
    def get(self, permission_id, version_id = None) -> dict:
        """
        Retrieve a permission by ID.
        :param permission_id: ID of the permission.
        :param version_id: ID of the version. Optional.
        :return: Permission.
        """
        if version_id:
            return self.britive.get(f'{self.base_url}/permissions/{permission_id}/{version_id}')
        else:
            return self.britive.get(f'{self.base_url}/permissions/{permission_id}')
    
    def delete(self, permission_id, version_id = None) -> dict:
        """
        Delete a permission.
        :param permission_id: ID of the permission.
        :param version_id: Version of the permission. Optional.
        :return: None
        """
        if version_id:
            return self.britive.delete(f'{self.base_url}/permissions/{permission_id}/{version_id}')
        else:
            return self.britive.delete(f'{self.base_url}/permissions/{permission_id}')
    
    def get_urls(self, permission_id) -> dict:
        """
        Retrieve URLs for a permission.
        :param permission_id: ID of the permission.
        :return: URLs.
        """
        return self.britive.get(f'{self.base_url}/permissions/get-urls/{permission_id}')
    
    def create(self, resource_type_id, name, description = '', checkin_file : bytes = None, checkout_file : bytes = None, variables = []) -> dict:
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

        
        params = {
            'resourceTypeId': resource_type_id,
            'name': name,
            'description': description,
            'isDraft': True,
        }
        permissionId = self.britive.post(f'{self.base_url}/permissions', json=params)['permissionId']
        urls = self.get_urls(permissionId)
        requests.put(urls['checkinURL'], files={'file': checkin_file})
        requests.put(urls['checkoutURL'], files={'file': checkout_file})
        params = {
            'checkinFileName' : permissionId + '_checkin',
            'checkoutFileName' : permissionId + '_checkout',
            'checkinTimeLimit' : 60,
            'checkoutTimeLimit' : 60,
            'createdBy' : 'Python-SDK',
            'description' : description,
            'inlineFileExists' : True,
            'isDraft' : False,
            'name' : name,
            'resourceTypeId' : resource_type_id,
            'updatedBy' : 'Python-SDK',
            'variables' : variables,
        }
        return self.britive.put(f'{self.base_url}/permissions/{permissionId}', json=params)
        