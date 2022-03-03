
class Accounts:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, application_id: str, environment_id: str = None,
             include_associations: bool = True, filter_expression: str = None) -> list:
        """
        Return details of all the accounts associated with a given application and environment.

        :param application_id: The ID of the application.
        :param environment_id: Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :param include_associations: Include the associated permissions and groups in the response.
        :param filter_expression: Filter based on `scanStatus`. Example: `scanStatus eq Unchanged`.
        :return: List containing details of each account.
        """

        params = {
            'page': 0,
            'size': 100,
            'includeMembers': include_associations
        }

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        if filter_expression:
            params['filter'] = filter_expression

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/accounts'
        return self.britive.get(url, params=params)

    def permissions(self, account_id: str, application_id: str,
                    environment_id: str = None, filter_expression: str = None) -> list:
        """
        Return details about the permissions associated to the specified account.

        :param account_id: The ID of the account.
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

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/accounts/{account_id}/permissions'
        return self.britive.get(url, params=params)

    def groups(self, account_id: str, application_id: str,
               environment_id: str = None, filter_expression: str = None) -> list:
        """
        Return details about the groups associated to the specified account.

        :param account_id: The ID of the account.
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

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/accounts/{account_id}/groups'
        return self.britive.get(url, params=params)

    def map(self, user_id: str, account_id: str, application_id: str, environment_id: str = None,
            map_user_to_account_in_all_application_environments: bool = False) -> list:
        """
        Associate a user (or users) with an account.

        :param user_id: The ID of the user you wish to map.
        :param account_id: The ID of the account.
        :param application_id: The ID of the application.
        :param environment_id:Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :param map_user_to_account_in_all_application_environments: If set to True will map the user to the specified
            account across all environments of the application.
        :return: List of mapped users for the account.
        """

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/accounts/{account_id}/users'

        if map_user_to_account_in_all_application_environments:
            url += f'/{user_id}'
            return self.britive.post(url, json={'saveToAllEnvs': True})
        else:
            return self.britive.post(url, json=[user_id])

    def unmap(self, user_id: str, account_id: str, application_id: str,
              environment_id: str = None, force_profile_checkins: bool = True) -> list:
        """
        Remove a user from an account.

        :param user_id: The ID of the user you wish to map.
        :param account_id: The ID of the account.
        :param application_id: The ID of the application.
        :param environment_id: Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :param force_profile_checkins: Force any currently checked out profiles for the user to be auto checked in.
            Will only check in profiles that are associated with the account being unmapped. Other profiles the user
            has will not be impacted.
        :return: List of mapped users for the account.
        """

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        params = {
            'forceCheckinPaps': force_profile_checkins
        }

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/accounts/{account_id}/users/{user_id}'
        return self.britive.delete(url, params=params)

    def mapped_users(self, account_id: str, application_id: str, environment_id: str = None) -> list:
        """
        Return a list of users who are mapped to the specified account.

        :param account_id: The ID of the account.
        :param application_id: The ID of the application.
        :param environment_id: Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :return: List of users mapped to the specified account.
        """

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/accounts/{account_id}/users'
        return self.britive.get(url)

    def users_available_to_map(self, account_id: str, application_id: str, environment_id: str = None) -> list:
        """
        Return a list of users available to be mapped to the specified account.

        :param account_id: The ID of the account.
        :param application_id: The ID of the application.
        :param environment_id: Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :return: List of users available to be mapped to the specified account.
        """

        params = {
            'page': 0,
            'size': 100,
            'query': 'available'
        }

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/accounts/{account_id}/users'
        return self.britive.get(url, params=params)
