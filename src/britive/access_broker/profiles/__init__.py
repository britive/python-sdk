from .permissions import Permissions
from .policies import Policies


class Profiles:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/profiles'
        self.permissions = Permissions(britive)
        self.policies = Policies(britive)

    def create(self, name: str, description: str = '', expiration_duration: int = 900000) -> dict:
        """
        Create a new profile.

        :param name: Name of the profile.
        :param description: Description of the profile.
        :param expiration_duration: Expiration duration of the profile.
        :return: Created profile.
        """

        params = {'name': name, 'description': description, 'expirationDuration': expiration_duration}

        return self.britive.post(f'{self.base_url}', json=params)

    def get(self, profile_id: str) -> dict:
        """
        Retrieve a profile by ID.

        :param profile_id: ID of the profile.
        :return: Profile.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}')

    def list(self) -> list:
        """
        Retrieve all profiles.

        :return: List of profiles.
        """

        return self.britive.get(self.base_url, params={})

    def update(
        self, profile_id: str, name: str = None, description: str = None, expiration_duration: int = None
    ) -> dict:
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

    def delete(self, profile_id: str) -> None:
        """
        Delete a profile.

        :param profile_id: ID of the profile.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{profile_id}')

    def add_association(self, profile_id: str, associations: dict = None) -> dict:
        """
        Add associations to a resource profile.

        :param profile_id: ID of the profile.
        :param associations: List of associations.
        :return: Updated profile.
        """

        if associations is None:
            associations = {}

        params = {'associations': associations}

        return self.britive.post(f'{self.base_url}/{profile_id}/associations', json=params)

    def list_associations(self, profile_id: str) -> list:
        """
        Retrieve all associations for a resource profile.

        :param profile_id: ID of the profile.
        :return: List of associations.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}/associations')

    def get_system_values(self, resource_type_id: str) -> dict:
        """
        Retrieve system values for a resource type.

        :param resource_type_id: ID of the resource type.
        :return: System values.
        """

        return self.britive.get(
            f'{self.base_url}/permissions/system-defined-values', params={'resourceTypeId': resource_type_id}
        )
