
class Tasks:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/tasks'

    def list(self, task_service_id: str) -> list:
        """
        Return a list of tasks for the given `task_service_id`.

        Make a call to `britive.task_services.get()` to obtain the appropriate `task_service_id`.

        :param task_service_id: The ID of the task service.
        :return: List of tasks.
        """

        return self.britive.get(f'{self.base_url}/services/{task_service_id}/tasks')

    def get(self, task_service_id: str, task_id: str) -> dict:
        """
        Return details of a task.

        Make a call to `britive.task_services.get()` to obtain the appropriate `task_service_id`.

        :param task_service_id: The ID of the task service.
        :param task_id: The ID of the task.
        :return: Details of the task.
        """

        return self.britive.get(f'{self.base_url}/services/{task_service_id}/tasks/{task_id}')[0]

    def create(self, task_service_id: str, name: str, properties: dict, frequency_type: str, start_time: str = None,
               frequency_interval: str = None) -> dict:
        """
        Create a new task.

        Make a call to `britive.task_services.get()` to obtain the appropriate `task_service_id`.

        :param task_service_id: The ID of the task service.
        :param name: The name of the task.
        :param properties: This parameter is dependent on the task service type. Currently only `environmentScanner` is
            supported. Below are details about how to properly set this parameter for `environmentScanner`.
            * appId: this is the appContainerId of the app to be scanned.
            * scope: This is a list of scopes. Each scope can be of type EnvironmentGroup or Environment.
            * orgScan: Boolean indicating whether an org scan must be done or not.

            {
                "appId": "app-id",
                "scope": [
                    {
                        "type": "EnvironmentGroup"|"Environment",
                        "value": "ID"
                    }
                ],
                "orgScan": true|false
            }
        :param frequency_type: Valid values are Daily, Weekly, Monthly, Hourly (start_time is implicitly the next hour).
        :param start_time: The start time of the task in GMT. Only applies to Daily, Weekly, and Monthly
            frequency types. Example: `12:00`.
        :param frequency_interval: Only applies to Weekly, Monthly, and Hourly frequency types.
            * Weekly: possible values are 1-7, which is Mon-Sun, respectively.
            * Monthly: possible values are from 1-31.
            * Hourly: possible values are 1-23.
        :return: Details of the newly created task.
        """

        data = {
            'name': name,
            'startTime': start_time,
            'frequencyType': frequency_type,
            'frequencyInterval': frequency_interval,
            'properties': properties
        }
        return self.britive.post(f'{self.base_url}/services/{task_service_id}/tasks', json=data)

    def statuses(self, task_service_id: str, task_id: str) -> list:
        """
        Return a list of task statuses ordered by `sentTime` (part of the response) desc.

        :param task_service_id: The ID of the task service.
        :param task_id: The ID of the task.
        :return: List of task statuses.
        """

        return self.britive.get(f'{self.base_url}/services/{task_service_id}/tasks/{task_id}/statuses')

    def update(self, task_service_id: str, task_id: str, name: str = None, properties: dict = None,
               frequency_type: str = None, start_time: str = None, frequency_interval: str = None) -> dict:
        """
        Updates a task.

        Only provide parameters that should be updated.

        Make a call to `britive.task_services.get()` to obtain the appropriate `task_service_id`.

        :param task_service_id: The ID of the task service.
        :param task_id: The ID of the task.
        :param name: The name of the task.
        :param properties: This parameter is dependent on the task service type. Currently only `environmentScanner` is
            supported. Below are details about how to properly set this parameter for `environmentScanner`.
            * appId: this is the appContainerId of the app to be scanned.
            * scope: This is a list of scopes. Each scope can be of type EnvironmentGroup or Environment.
            * orgScan: Boolean indicating whether an org scan must be done or not.

            {
                "appId": "app-id",
                "scope": [
                    {
                        "type": "EnvironmentGroup"|"Environment",
                        "value": "ID"
                    }
                ],
                "orgScan": true|false
            }
        :param frequency_type: Valid values are Daily, Weekly, Monthly, Hourly (start_time is implicitly the next hour).
        :param start_time: The start time of the task in GMT. Only applies to Daily, Weekly, and Monthly
            frequency types. Example: `12:00`.
        :param frequency_interval: Only applies to Weekly, Monthly, and Hourly frequency types.
            * Weekly: possible values are 1-7, which is Mon-Sun, respectively.
            * Monthly: possible values are from 1-31.
            * Hourly: possible values are 1-23.
        :return: Details of the newly created task.
        """

        # construct the dict assuming every parameter is present
        raw_data = {
            'name': name,
            'startTime': start_time,
            'frequencyType': frequency_type,
            'frequencyInterval': frequency_interval,
            'properties': properties
        }

        # and now remove any None values
        data = {k: v for k, v in raw_data.items() if v is not None}

        return self.britive.patch(f'{self.base_url}/services/{task_service_id}/tasks/{task_id}', json=data)

    def delete(self, task_service_id: str, task_id: str) -> None:
        """
        Delete a task.

        :param task_service_id: The ID of the task service.
        :param task_id: The ID of the task.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/services/{task_service_id}/tasks/{task_id}')

