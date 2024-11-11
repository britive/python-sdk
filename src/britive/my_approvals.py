class MyApprovals:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/approvals'

    def approve_request(self, request_id: str, comments: str = '') -> None:
        """
        Approves a request.

        :param request_id: The ID of the request.
        :param comments: Approver comments.
        :return: None.
        """

        params = {'approveRequest': 'yes'}
        data = {'approverComment': comments}

        return self.britive.patch(f'{self.britive.base_url}/{request_id}', params=params, json=data)

    def reject_request(self, request_id: str, comments: str = '') -> None:
        """
        Rejects a request.

        :param request_id: The ID of the request.
        :param comments: Approver comments.
        :return: None.
        """

        params = {'approveRequest': 'no'}
        data = {'approverComment': comments}

        return self.britive.patch(f'{self.britive.base_url}/{request_id}', params=params, json=data)

    def list_approvals(self) -> dict:
        """
        Lists approval requests.

        :return: List of approval requests.
        """

        params = {'requestType': 'myApprovals', 'consumer': 'papservice'}

        return self.britive.get(f'{self.britive.base_url}', params=params)
