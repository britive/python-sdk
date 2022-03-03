class Environments:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def create(self, application_id: str, name: str, description: str = None, parent_group_id: str = None) -> dict:
        """
        Create a new environment inside the specified application.

        Only applicable to applications which have `catalogApplication.supportsEnvironmentScanning` set to `False`.

        :param application_id: The ID of the application inside of which the environment will be created.
        :param name: The name of the environment.
        :param description: An optional description of the environment.
        :param parent_group_id: An optional parent group id - if not provided then the root group is assumed and will
            be created as needed.
        :return: Details of the newly created environment.
        """

        data = {
            'name': name,
            'type': 'environment',
            'description': description or '',
            'parentGroupId': parent_group_id or self.britive.environment_groups.get_or_create_root(
                application_id=application_id
            )
        }

        return self.britive.post(f'{self.base_url}/{application_id}/root-environment-group/environments', json=data)

    def get(self, application_id: str, environment_id: str) -> dict:
        """
        Return details about the specified environment.

        :param application_id: The ID of the application where the environment resides.
        :param environment_id: The ID of the environment.
        :return: Details about the environment.
        """

        envs = self.list(application_id=application_id)
        for env in envs:
            if env['environmentId'] == environment_id:
                return env
        return {}

    def list(self, application_id: str) -> list:
        """
        Return a list of environments for the specified application.

        :param application_id: The ID of the application.
        :return: List of environments.
        """

        return self.britive.get(f'{self.base_url}/{application_id}/environments')

    def test(self, application_id: str, environment_id: str) -> dict:
        """
        Test the settings of the specified environment.

        :param application_id: The ID of the application containing the environment to test.
        :param environment_id: The ID fo the environment to test.
        :return: Results of the test. Failures will not throw errors - rather the failure message
            will be in the response.
        """

        return self.britive.post(f'{self.base_url}/{application_id}/environments/{environment_id}/tests')

    def update(self, application_id: str, environment_id: str,  **kwargs) -> dict:
        """
        Update the supplied properties of the environment.

        :param application_id: The ID of the application to update.
        :param environment_id: The ID of the environment to update.
        :param kwargs: A set of name/value pairs where the property name will be updated to the supplied value.
            Property names are dependent upon the catalog application. Call method `environment.get()` and review
            the attribute `catalogApplication.propertyTypes` for a list of acceptable names to use here.
        :return: Details of the updated environment.
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
        return self.britive.patch(
            f'{self.base_url}/{application_id}/environments/{environment_id}/properties',
            json=data
        )

    def scan(self, application_id: str, environment_id: str) -> dict:
        """
        Initiate a scan of the environment. Required only for applications which have
        `catalogApplication.supportsEnvironmentScanning` set to `False`.

        For all other application types the application will be scanned and not the underlying environment(s).

        Scans are asynchronous operations. The response will include a `taskId` which can be used to make calls
        to `britive.scans.status()` to obtain the current status of the scan.

        Note that scans can also be initiated from the Scans class. The same type of scan will be performed no matter
        where it is initiated.

        :param application_id: The ID of the application to scan.
        :param environment_id: The ID of the environment to scan.
        :return: Details of the scan that was initiated.
        """

        return self.britive.scans.scan(application_id=application_id, environment_id=environment_id)

    def delete(self, application_id: str, environment_id: str) -> None:
        """
        Delete the specified environment.

        :param application_id: The ID of the application containing the environment to delete.
        :param environment_id: The ID of the environment to delete.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{application_id}/environments/{environment_id}')


