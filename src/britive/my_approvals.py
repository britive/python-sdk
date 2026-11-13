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

    def approve_request(self, request_id: str, comments: str = '', headers: dict = None) -> None:
        """
        Approves a request.

        :param request_id: The ID of the request.
        :param comments: Approver comments.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: None.
        """

        params = {'approveRequest': 'yes'}
        data = {'approverComment': comments}

        return self.britive.patch(f'{self.base_url}/{request_id}', params=params, json=data, headers=headers)

    def reject_request(self, request_id: str, comments: str = '', headers: dict = None) -> None:
        """
        Rejects a request.

        :param request_id: The ID of the request.
        :param comments: Approver comments.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: None.
        """

        params = {'approveRequest': 'no'}
        data = {'approverComment': comments}

        return self.britive.patch(f'{self.base_url}/{request_id}', params=params, json=data, headers=headers)

    def revoke_request(
        self, request_id: str, comments: str = '', kill_session: bool = False, headers: dict = None
    ) -> None:
        """Revoke an approved request.

        :param request_id: The ID of the request.
        :param comments: Revoker comments.
        :param kill_session: Also end the access session granted by the request.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: None.
        """
        params = {'approveRequest': 'revoke', 'killSession': 'true' if kill_session else 'false'}
        data = {'revokerComment': comments}
        return self.britive.patch(f'{self.base_url}/{request_id}', params=params, json=data, headers=headers)

    def revoke_requests(
        self, request_ids: list, comments: str, kill_session: bool = False, headers: dict = None
    ) -> dict:
        """Revoke several approved requests.

        :param request_ids: The IDs of the requests.
        :param comments: Revoker comments.
        :param kill_session: Also end the access sessions granted by the requests.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: Dict with a `success` list of request IDs and a `failed` map of request IDs to error messages.
            The API processes each request separately. A successful HTTP response can contain failed revocations;
            callers must inspect `failed`. This operation is not atomic.
        """
        data = {'approvals': request_ids, 'revokerComment': comments, 'killSession': kill_session}
        return self.britive.post(f'{self.base_url}/revoke', json=data, headers=headers)

    def get(self, request_id: str, headers: dict = None) -> dict:
        """Return an approval request, including each approver's status.

        :param request_id: The ID of the request.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: Details of the approval request.
        """
        return self.britive.get(f'{self.base_url}/{request_id}', params={'requestType': 'myApprovals'}, headers=headers)

    def get_profile_permissions(self, profile_id: str, environment_id: str, headers: dict = None) -> list:
        """Return the permissions a profile grants in an environment.

        :param profile_id: The ID of the profile.
        :param environment_id: The ID of the environment.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: List of permissions for reviewing a profile checkout request.
        """
        return self.britive.get(
            f'{self.britive.base_url}/access/environments/{environment_id}/profiles/{profile_id}/permissions',
            headers=headers,
        )

    def get_resource_labels(self, resource_id: str, headers: dict = None) -> dict:
        """Return a resource's labels for reviewing a resource checkout request.

        :param resource_id: The ID of the resource.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: Dict of resource labels.
        """
        return self.britive.get(
            f'{self.britive.base_url}/resource-manager/{resource_id}/label-details', headers=headers
        )

    def list_tag_request_grants(self, tag_id: str, grant_type: str, headers: dict = None) -> list:
        """Return what membership of a tag grants.

        :param tag_id: The ID of the tag.
        :param grant_type: One of `app-profiles`, `resources`, or `secrets`.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: List of the application profiles, resources, or secrets the tag grants.
        """
        if grant_type not in ('app-profiles', 'resources', 'secrets'):
            raise ValueError('grant_type must be one of app-profiles, resources or secrets.')
        return self.britive.get(f'{self.britive.base_url}/access-requests/tags/{tag_id}/{grant_type}', headers=headers)

    def list(
        self,
        headers: dict = None,
        *,
        active_status: str = None,
        created_within_days: int = None,
        filter_text: str = None,
    ) -> list:
        """
        Lists approval requests.

        :param active_status: One of `all`, `active`, or `inactive`.
        :param created_within_days: Only list requests created within this many days.
        :param filter_text: Filter expression.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: List of approval requests.
        """

        params = {
            'requestType': 'myApprovals',
            'activeStatus': active_status,
            'createdWithinDays': created_within_days,
            'filter': filter_text,
        }

        return self.britive.get(
            f'{self.base_url}/', params={k: v for k, v in params.items() if v is not None}, headers=headers
        )
