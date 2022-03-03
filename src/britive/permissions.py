
class Permissions:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, application_id: str, environment_id: str = None,
             include_associations: bool = True, filter_expression: str = None) -> list:
        """
        Return details of all the permissions associated with a given application and environment.

        :param application_id: The ID of the application.
        :param environment_id: Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :param include_associations: Include the associated accounts and groups in the response.
        :param filter_expression: Filter based on `scanStatus`. Example: `scanStatus eq Unchanged`.
        :return: List containing details of each permission.
        """

        params = {
            'page': 0,
            'size': 100,
            'includeMembers': include_associations
        }

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        if filter_expression:
            params['filter'] = filter_expression

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/permissions'
        return self.britive.get(url, params=params)

    def accounts(self, permission_id: str, application_id: str,
                 environment_id: str = None, filter_expression: str = None) -> list:
        """
        Return details about the accounts associated with the specified permission.

        :param permission_id: The ID of the permission.
        :param application_id: The ID of the application.
        :param environment_id: Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :param filter_expression: Filter based on `scanStatus`. Example: `scanStatus eq Unchanged`.
        :return: List of permissions associated with the specified account.
        """

        params = {
            'page': 0,
            'size': 100
        }

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        if filter_expression:
            params['filter'] = filter_expression

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/permissions/{permission_id}/accounts'
        return self.britive.get(url, params=params)

    def groups(self, permission_id: str, application_id: str,
               environment_id: str = None, filter_expression: str = None) -> list:
        """
        Return details about the groups associated to the specified account.

        :param permission_id: The ID of the permission.
        :param application_id: The ID of the application.
        :param environment_id: Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :param filter_expression: Filter based on `scanStatus`. Example: `scanStatus eq Unchanged`.
        :return: List of groups associated with the specified account.
        """

        params = {
            'page': 0,
            'size': 100
        }

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        if filter_expression:
            params['filter'] = filter_expression

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/permissions/{permission_id}/groups'
        return self.britive.get(url, params=params)
