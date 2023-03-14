
class SystemConsumers:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/policy-admin/consumers'

    def list(self) -> list:
        """
        List system level consumers.

        :returns: List of consumers.
        """

        return self.britive.get(self.base_url)['result']


