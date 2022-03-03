
class Scans:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def scan(self, application_id: str, environment_id: str = None) -> dict:
        """
        Initiate a scan of the provided application and optionally provided environment.

        `environment_id` is only required only for applications which have
        `catalogApplication.supportsEnvironmentScanning` set to `False`.

        Scans are asynchronous operations. The response will include a `taskId` which can be used to make calls
        to `Scans.status()` to obtain the current status of the scan.

        Note that scans can also be initiated from the Applications and Environments classes. The same type of
        scan will be performed no matter where it is initiated.

        :param application_id: The ID of the application to scan.
        :param environment_id: Optionally the ID of the environment to scan.
        :return: Details of the scan that was initiated.
        """

        if environment_id:
            return self.britive.post(f'{self.base_url}/{application_id}/environments/{environment_id}/scans')
        else:
            return self.britive.post(f'{self.base_url}/{application_id}/scan')

    def status(self, task_id: str) -> dict:
        """
        Provide details on the current status of a scan.

        :param task_id: The ID of the task which was obtained when a scan was initiated.
        :return: Details on the current status of the scan.
        """

        return self.britive.get(f'{self.base_url}/tasks/{task_id}/status')

    def history(self, application_id: str, filter_expression: str = None) -> list:
        """
        Return a list of all scans in the past 90 days for the application ID provided.

        :param application_id: The ID of the application for which scan history will be retrieved.
        :param filter_expression: Optional filter expression to filter the results server side. Can filter based
            on `name`, `status`, and `integrity checks`. The supported operators are `eq` and `co`.
            Example: `name co "Dev Account"`.
        :return: A list of historical scans.
        """

        params = {
            'page': 0,
            'size': 100
        }
        if filter_expression:
            params['filter'] = filter_expression
        return self.britive.get(f'{self.base_url}/{application_id}/scans/env-status/history', params=params)

    def diff(self, resource: str, application_id: str, environment_id: str = None) -> list:
        """
        Retrieve changes between the last two consecutive scans.

        :param resource: valid options are `permissions`, `groups`, and `accounts`.
        :param application_id: The ID of the application.
        :param environment_id: Optionally the ID of the environment. Required only for applications which have
            `catalogApplication.supportsEnvironmentScanning` set to `False`.
        :return: List of changes between the last two consecutive scans of the given resource.
        """

        if resource not in ['permissions', 'groups', 'accounts']:
            raise ValueError(f'invalid resource {resource}')

        environment_id = environment_id or self.britive.get_root_environment_group(application_id)

        url = f'{self.base_url}/{application_id}/environments/{environment_id}/{resource}/memberships-last-scan-delta'
        return self.britive.get(url)
