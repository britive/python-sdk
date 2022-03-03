
class Groups:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, application_id: str, environment_id: str = None,
             include_associations: bool = True, filter_expression: str = None) -> list:
        """
        Returnsdetails of all the groups associated with a given application and environment.

        :param application_id: The ID of the application.
        :param environment_id: Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :param include_associations: Include the associated permissions and accounts in the response.
        :param filter_expression: Filter based on `scanStatus`. Example: `scanStatus eq Unchanged`.
        :return: List containing details of each group.
        """

        params = {
            'page': 0,
            'size': 100,
            'includeMembers': include_associations
        }

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        if filter_expression:
            params['filter'] = filter_expression

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/groups'
        return self.britive.get(url, params=params)

    def accounts(self, group_id: str, application_id: str,
                 environment_id: str = None, filter_expression: str = None) -> list:
        """
        Return details about the accounts associated with the specified group.

        :param group_id: The ID of the group.
        :param application_id: The ID of the application.
        :param environment_id: Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :param filter_expression: Filter based on `scanStatus`. Example: `scanStatus eq Unchanged`.
        :return: List of accounts associated with the specified group.
        """

        params = {
            'page': 0,
            'size': 100
        }

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        if filter_expression:
            params['filter'] = filter_expression

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/groups/{group_id}/accounts'
        return self.britive.get(url, params=params)

    def permissions(self, group_id: str, application_id: str,
                    environment_id: str = None, filter_expression: str = None) -> list:
        """
        Return details about the permissions associated with the specified group.

        :param group_id: The ID of the group.
        :param application_id: The ID of the application.
        :param environment_id: Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :param filter_expression: Filter based on `scanStatus`. Example: `scanStatus eq Unchanged`.
        :return: List of permissions associated with the specified group.
        """
        
        params = {
            'page': 0,
            'size': 100
        }

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        if filter_expression:
            params['filter'] = filter_expression

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/groups/{group_id}/permissions'
        return self.britive.get(url, params=params)
