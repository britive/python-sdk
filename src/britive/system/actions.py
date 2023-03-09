
class SystemActions:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/policy-admin/actions'

    def list(self, consumer: str = None) -> list:
        """
        List system level actions.

        :param consumer: The consumer for which the list should be filtered.
        :returns: List of actions.
        """

        params = {}
        if consumer:
            params['filter'] = f'consumer eq {consumer}'
        return self.britive.get(self.base_url, params=params)['result']


