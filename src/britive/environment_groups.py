
class EnvironmentGroups:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def create(self, application_id: str, name: str, description: str = None, parent_id: str = None) -> dict:
        """
        Create a new environment group inside the specified application.

        Only applicable to applications which have `catalogApplication.supportsEnvironmentScanning` set to `False`.

        :param application_id: The ID of the application inside of which the environment group will be created.
        :param name: The name of the environment group.
        :param description: An optional description of the environment group.
        :param parent_id: An optional parent group id - if not provided then the root group is assumed and will
            be created as needed.
        :return: Details of the newly created environment group.
        """

        data = {
            'name': name,
            'type': 'group',
            'description': description or '',
            'parentId': parent_id or self.get_or_create_root(application_id=application_id)
        }

        return self.britive.post(f'{self.base_url}/{application_id}/root-environment-group/groups', json=data)

    def get_or_create_root(self, application_id: str) -> str:
        """
        Returns the ID of the root environment group. Will only create one if one does not already exist.

        A root environment group is NOT automatically created at application creation. For applications which
        support environments and environment groups (`catalogApplication.supportsEnvironmentScanning` set to `False`)
        the root group has to be created before the first environment/environment group can be created. That will be
        handled by this method and is internal to this SDK - the end user would generally not need to  interact with
        this method. Instead the logic inside of EnvironmentGroups.create() and Environments.create() handles the
        creation of the root group as required.

        :param application_id: The ID of the application under which to create the root environment group.
        :return: ID of the root environment group for the given application.
        """

        groups = self.list(application_id=application_id)
        root_id = None
        for group in groups:
            if group['name'].lower() == 'root' and group['parentId'] == '' and group['type'] == 'group':
                root_id = group['id']
                break

        if not root_id:
            data = {
                'name': 'root',
                'type': 'group',
                'description': '',
                'parentId': ''
            }

            root_id = self.britive.post(
                f'{self.base_url}/{application_id}/root-environment-group/groups',
                json=data
            )['id']

        return root_id

    def get(self, application_id: str, environment_group_id: str) -> dict:
        """
        Return details about the specified environment group.

        :param application_id: The ID of the application where the environment group resides.
        :param environment_group_id: The ID of the environment group.
        :return: Details about the specified environment group.
        """

        groups = self.list(application_id=application_id)
        for group in groups:
            if group['id'] == environment_group_id:
                return group
        return {}

    def list(self, application_id: str) -> list:
        """
        Return a list of environment groups for the specified application.

        :param application_id: The ID of the application.
        :return: List of environment groups.
        """

        app = self.britive.get(f'{self.base_url}/{application_id}')
        root_env_group = app.get('rootEnvironmentGroup', {}) or {}
        groups = root_env_group.get('environmentGroups')
        return groups or []

    def delete(self, application_id: str, environment_group_id: str) -> None:
        """
        Delete the specified environment group.

        :param application_id: The ID of the application containing the environment group to delete.
        :param environment_group_id: The ID of the environment group to delete.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{application_id}/environment-groups/{environment_group_id}')



