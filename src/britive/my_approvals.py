class MyApprovals:
    """
    This class is meant to be called by end users. It is an API layer on top of the actions that can be performed on the
    "My Approvals" page of the Britive UI.

    No "administrative" access is required by the methods in this class. Each method will only return approvals/allow
    actions which are permitted to be performed by the user/service identity, as identified by an API token or
    interactive login bearer token.

    It is entirely possible that an administrator who makes these API calls could get nothing returned, as that
    administrator may not have any pending approvals.
    """

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

        return self.britive.patch(f'{self.base_url}/{request_id}', params=params, json=data)

    def reject_request(self, request_id: str, comments: str = '') -> None:
        """
        Rejects a request.

        :param request_id: The ID of the request.
        :param comments: Approver comments.
        :return: None.
        """

        params = {'approveRequest': 'no'}
        data = {'approverComment': comments}

        return self.britive.patch(f'{self.base_url}/{request_id}', params=params, json=data)

    def list(self) -> dict:
        """
        Lists approval requests.

        :return: List of approval requests.
        """

        params = {'requestType': 'myApprovals'}

        return self.britive.get(f'{self.base_url}/', params=params)
