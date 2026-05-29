class Types:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/resource-types'
        self.scheduled_scan_base_url = f'{self.britive.base_url}/tasks/services/resource-scan'

    def create(self, name: str, description: str = '', fields: list = None) -> dict:
        """
        Create a new resource type.

        :param name: Name of the resource type.
        :param description: Description of the resource type.
        :param fields: List of Resource Type fields.
            Example: [
                {
                    'name': 'string',
                    'paramType': 'string'|'multiline'|'password'|'ip-cidr'|'regex'|'list',
                    'isMandatory': True|False
                },
                ...
            ]
        :return: Created resource type.
        """
        params = {
            'name': name,
            'description': description,
        }

        if fields:
            params['parameters'] = fields

        return self.britive.post(self.base_url, json=params)

    def get(self, resource_type_id: str) -> dict:
        """
        Retrieve a resource type by ID.

        :param resource_type_id: ID of the resource type.
        :return: Resource type.
        """
        return self.britive.get(f'{self.base_url}/{resource_type_id}')

    def list(self) -> list:
        """
        Retrieve all resource types.

        :return: List of resource types.
        """

        return self.britive.get(self.base_url)['data']

    def update(self, resource_type_id: str, description: str = None, fields: list = None) -> dict:
        """
        Update a resource type.

        :param resource_type_id: ID of the resource type.
        :param description: Description of the resource type.
        :param fields: List of Resource Type fields.
            Example: [
                {
                    'name': 'string',
                    'paramType': 'string'|'multiline'|'password'|'ip-cidr'|'regex'|'list',
                    'isMandatory': True|False
                },
                ...
            ]
        :return: Updated resource type.
        """
        params = {'name': self.get(resource_type_id=resource_type_id)['name']}

        if description:
            params['description'] = description
        if fields:
            params['parameters'] = fields

        return self.britive.put(f'{self.base_url}/{resource_type_id}', json=params)

    def delete(self, resource_type_id: str) -> None:
        """
        Delete a resource type.

        :param resource_type_id: ID of the resource type.
        :return: None
        """
        return self.britive.delete(f'{self.base_url}/{resource_type_id}')

    def scan(self, resource_type_id: str, resource_labels: list = None) -> dict:
        """
        Trigger a broker scan for resources of the given resource type.

        When called without `resource_labels`, all resources of the resource type are scanned.
        When called with `resource_labels`, only resources matching the provided labels are scanned.

        :param resource_type_id: ID of the resource type.
        :param resource_labels: Optional list of resource label dicts to filter which resources to scan.
            Example: [{'key': 'env', 'label-values': ['prod', 'staging']}]
        :return: Details of the scan that was initiated.
        """

        params = {}
        if resource_labels:
            params['resourceLabels'] = resource_labels
        return self.britive.post(f'{self.base_url}/{resource_type_id}/scan', json=params)

    def get_scan_settings(self, resource_type_id: str) -> dict:
        """
        Retrieve scan settings for a resource type.

        :param resource_type_id: ID of the resource type.
        :return: Scan settings for the resource type.
        """

        return self.britive.get(f'{self.base_url}/{resource_type_id}/scan-settings')

    def get_scheduled_scan_service(self, resource_type_id: str) -> dict:
        """
        Retrieve the scheduled scan service for a resource type.

        The scheduled scan service manages all scheduled scan tasks for a given resource type.
        Use the returned service ID with `list_scheduled_scans`, `enable_scheduled_scans`,
        `disable_scheduled_scans`, and `delete_scheduled_scan`.

        :param resource_type_id: ID of the resource type.
        :return: Scheduled scan service details.
        """

        return self.britive.get(f'{self.scheduled_scan_base_url}/resource-types/{resource_type_id}')

    def create_scheduled_scan(self, resource_type_id: str, name: str, description: str = '',
                              frequency: str = 'Daily', frequency_interval: int = None,
                              start_time: str = '12:00', resource_labels: list = None) -> dict:
        """
        Create a new scheduled scan task for a resource type.

        :param resource_type_id: ID of the resource type.
        :param name: Name of the scheduled scan.
        :param description: Optional description for the scheduled scan.
        :param frequency: Frequency of the scan. One of 'Daily', 'Weekly', or 'Monthly'. Defaults to 'Daily'.
        :param frequency_interval: Required for Weekly (0=Sunday..6=Saturday) and Monthly (1-31 day of month).
            Not used for Daily.
        :param start_time: Time of day to run the scan in HH:MM format in UTC. Defaults to '12:00'.
        :param resource_labels: Optional list of resource label dicts to filter which resources to scan.
            Example: [{'key': 'env', 'label-values': ['prod', 'staging']}]
        :return: Details of the created scheduled scan task.
        """

        task = {
            'name': name,
            'description': description,
            'properties': {},
            'frequencyType': frequency,
            'frequencyInterval': frequency_interval,
            'startTime': start_time,
        }
        if resource_labels:
            task['properties']['resourceLabels'] = resource_labels
        params = {
            'taskService': {
                'name': 'ResourceScanner',
                'enabled': False,
                'queueId': 'resourceScannerQueue',
            },
            'task': task,
        }
        return self.britive.post(f'{self.scheduled_scan_base_url}/resource-types/{resource_type_id}', json=params)

    def list_scheduled_scans(self, service_id: str) -> list:
        """
        List all scheduled scan tasks for a scheduled scan service.

        :param service_id: ID of the scheduled scan service (from `get_scheduled_scan_service`).
        :return: List of scheduled scan tasks.
        """

        return self.britive.get(f'{self.scheduled_scan_base_url}/{service_id}/tasks')

    def enable_scheduled_scans(self, service_id: str) -> dict:
        """
        Enable scheduled scans for a scheduled scan service.

        :param service_id: ID of the scheduled scan service (from `get_scheduled_scan_service`).
        :return: Details of the enabled service.
        """

        return self.britive.post(f'{self.scheduled_scan_base_url}/{service_id}/enabled-statuses')

    def disable_scheduled_scans(self, service_id: str) -> dict:
        """
        Disable scheduled scans for a scheduled scan service.

        :param service_id: ID of the scheduled scan service (from `get_scheduled_scan_service`).
        :return: Details of the disabled service.
        """

        return self.britive.post(f'{self.scheduled_scan_base_url}/{service_id}/disabled-statuses')

    def delete_scheduled_scan(self, service_id: str, task_id: str) -> None:
        """
        Delete a scheduled scan task.

        :param service_id: ID of the scheduled scan service (from `get_scheduled_scan_service`).
        :param task_id: ID of the scheduled scan task to delete.
        :return: None
        """

        return self.britive.delete(f'{self.scheduled_scan_base_url}/{service_id}/tasks/{task_id}')
