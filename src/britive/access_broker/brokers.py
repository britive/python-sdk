class Brokers:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/remote-broker/brokers'

    def list(self, status: str = '') -> list:
        """
        List brokers with ability to filter by status.

        :param status: Filter brokers by a list of statuses, combining the statuses using an OR condition.
            The statuses are case-sensitive.
            Possible values are `active`, `inactive`, and `disconnected`.
            Provide values as a comma-separated list to apply an OR filter (e.g., `status=active,inactive`).
        :return: List of brokers.
        """

        params = {
            'status': status,
        }

        return self.britive.get(self.base_url, params=params)['data']
