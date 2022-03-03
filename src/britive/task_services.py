
class TaskServices:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/tasks/services'

    def get(self, application_id: str, service_name: str = 'environmentScanner') -> dict:
        """
        Retrieve details of the task scheduler service associated with `application_id`.

        A task service is automatically created when a new application is created. A task service cannot be created
        independent of an application.

        :param application_id: The ID of the application.
        :param service_name: The name of the task scheduler service. Currently only `environmentScanner` is supported
            but this parameter exists in case future application releases introduce other service types.
        :return: Details of the task scheduler service.
        """

        params = {
            'name': service_name,
            'appId': application_id
        }
        return self.britive.get(f'{self.base_url}', params=params)

    def enable(self, task_service_id: str) -> dict:
        """
        Enable a task service.

        :param task_service_id: The ID of the task service.
        :return: Details of the newly enabled task service.
        """

        return self.britive.post(f'{self.base_url}/{task_service_id}/enabled-statuses')

    def disable(self, task_service_id: str) -> dict:
        """
        Disable a task service.

        :param task_service_id: The ID of the task service.
        :return: Details of the newly disabled task service.
        """

        return self.britive.post(f'{self.base_url}/{task_service_id}/disabled-statuses')