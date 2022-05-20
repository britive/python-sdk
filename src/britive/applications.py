valid_user_account_mappings = {
    'email': [
        {
            'name': 'email',
            'description': 'Email'
        }
    ],
    'username': [
        {
            'name': 'username',
            'description': 'Username'
        }
    ]
}


class Applications:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, extended: bool = True) -> list:
        """
        Return a list of applications in the Britive tenant.

        :param extended: if True, will return additional details of the applications
        :return: List of applications.
        """

        params = {}
        if extended:
            params['view'] = 'extended'
        return self.britive.get(self.base_url, params=params)

    def get(self, application_id: str) -> dict:
        """
        Return details of the specified application

        :param application_id: The ID of the application.
        :return: Details of the application.
        """

        return self.britive.get(f'{self.base_url}/{application_id}')

    def catalog(self) -> list:
        """
        Return a list of applications in the application catalog.

        All applications in the tenant will derive from one of the applications returned.

        :return: List of applications in the application catalog
        """

        options = self.britive.get(f'{self.britive.base_url}/system/apps')
        return [o for o in options if o['catalogAppId'] != 0]

    def create(self, catalog_id: int, application_name: str) -> dict:
        """
        Create a new application.

        :param catalog_id: The ID of the catalog application from which to create the new application. Make a call to
            `catalog` to retrieve the list of applications in the catalog.
        :param application_name: The unique name for the application being created.
        :return: Details of the created application.
        """

        data = {
            'catalogAppId': catalog_id,
            'catalogAppDisplayName': application_name
        }

        return self.britive.post(self.base_url, json=data)

    def set_user_account_mapping(self, application_id: str, user_account_mapping: str = None) -> dict:
        """
        Set the user-to-account mapping attribute of the application.

        :param application_id: The ID of the application to update.
        :param user_account_mapping: The user-to-account mapping from Britive to the destination
            cloud provider identity. Valid values are `email`, `username`, and None.
        :return:
        """

        if user_account_mapping and user_account_mapping not in valid_user_account_mappings.keys():
            raise ValueError('invalid user_account_mapping value')

        data = {
            'userAccountMappings': valid_user_account_mappings.get(user_account_mapping, [])
        }
        self.britive.post(f'{self.base_url}/{application_id}/user-account-mappings', json=data)
        return self.get(application_id=application_id)

    def enable(self, application_id: str) -> dict:
        """
        Enable an application.

        :param application_id: The ID of the application to enable.
        :return: Details of the newly enabled application.
        """

        data = {
            'status': 'active'
        }
        return self.britive.patch(f'{self.base_url}/{application_id}', json=data)

    def disable(self, application_id: str) -> dict:
        """
        Disable an application.

        :param application_id: The ID of the application to disable.
        :return: Details of the newly disabled application.
        """

        data = {
            'status': 'inactive'
        }
        return self.britive.patch(f'{self.base_url}/{application_id}', json=data)

    def test(self, application_id: str) -> dict:
        """
        Test an application configuration.

        This operation performs configuration checks to ensure that the application is correctly configured.

        :param application_id: The ID of the application to test.
        :return: A dict containing 2 keys - `success` and `message`.
        """

        return self.britive.get(f'{self.base_url}/{application_id}/test')

    def update(self, application_id: str, **kwargs) -> dict:
        """
        Update an application.

        :param application_id: The ID of the application to update.
        :param kwargs: A set of name/value pairs where the property name will be updated to the supplied value.
            Property names are dependent upon the catalog application. Call method `applications.catalog()` for a list
            of all catalog applications, find the catalog application in question, and review the attribute
            `propertyTypes` for a list of acceptable names to use here.
        :return: Details of the updated application.
        """

        data = {
            'propertyTypes': []
        }
        for key, value in kwargs.items():
            data['propertyTypes'].append(
                {
                    'name': key,
                    'value': value,
                    'defaultValue': value
                }
            )
        return self.britive.patch(f'{self.base_url}/{application_id}/properties', json=data)

    def scan(self, application_id: str) -> dict:
        """
        Initiate a scan of the application.

        For applications which have `catalogApplication.supportsEnvironmentScanning` set to `False` do not scan the
        application. Instead scan the environment(s) associated with the application.

        For AWS (not AWS standalone) application types, this method will initiate an organization scan to collect
        the accounts in the org and their place in the OU structure.

        Scans are asynchronous operations. The response will include a `taskId` which can be used to make calls
        to `britive.scans.status()` to obtain the current status of the scan.

        Note that scans can also be initiated from the Scans class. The same type of scan will be performed no matter
        where it is initiated.

        :param application_id: The ID of the application to scan.
        :return: Details of the scan that was initiated.
        """

        return self.britive.scans.scan(application_id=application_id)

    def delete(self, application_id: str) -> None:
        """
        Delete an application.

        Will also recursively delete any environments, environment groups, accounts, profiles, etc. which are a part
        of the application.

        :param application_id: The ID of the application to delete.
        :return: None
        """

        params = {
            'appContainerId': application_id
        }
        return self.britive.delete(self.base_url, params=params)