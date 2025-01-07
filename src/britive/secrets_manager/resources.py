class Resources:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager/resourceContainers'

    def get(self, path: str = '/') -> dict:
        """
        Gets a resource from the vault

        :param path: path of the resource, include the / at the beginning
        :return: Details of the resource.
        """

        params = {'path': path}
        return self.britive.get(f'{self.base_url}', params=params)
