class Requests():
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/approvals'

    def get(self, request_id: str) -> dict:
        """
        Provides details of given request.

        :param request_id: ID of the request.
        :return: Details of specified request.
        """

        return self.britive.get(f'{self.base_url}/{request_id}')

    def list(self, filter : str = None) -> list:
        """
        Return the list of requests.

        :param filter: The filter that can filter the list requests. The supported operators are 'eq' and 'co'.
        :return: list of requests
        """

        params = {
            'requestType' : 'myRequests',
            'filter' : filter
        }

        return self.britive.get(self.base_url, params=params)