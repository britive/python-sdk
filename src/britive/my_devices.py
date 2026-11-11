from .exceptions import (
    ApprovalRequiredButNoJustificationProvided,
    ProfileCheckoutAlreadyApproved,
    StepUpAuthFailed,
    StepUpAuthRequiredButNotProvided,
)
from .exceptions.badrequest import ApprovalJustificationRequiredError, ProfileApprovalRequiredError
from .exceptions.generic import StepUpAuthenticationRequiredError


class MyDevices:
    """
    This class is meant to be called by end users. It is an API layer on top of the actions that can be performed on the
    "My Devices" page of the Britive UI.

    No "administrative" access is required by the methods in this class. Each method will only return devices/allow
    actions which are permitted to be performed by the user/service identity, as identified by an API token or
    interactive login bearer token.
    """

    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/access'

    def list(
        self,
        filter_text: str = None,
        search_text: str = None,
        page: int = None,
        size: int = None,
        headers: dict = None,
    ) -> dict:
        """
        List the device profiles the user has access to.

        :param filter_text: Filter the results.
        :param search_text: Search the results.
        :param page: The page number to return.
        :param size: The number of results per page.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: Dict with a `data` list of device profiles and paging details.
        """

        params = {
            'filter': filter_text,
            'searchText': search_text,
            'page': page,
            'size': size,
        }

        return self.britive.get(
            f'{self.base_url}/devices',
            params={k: v for k, v in params.items() if v is not None},
            headers=headers,
            pagination='none',
        )

    def checkout(
        self,
        profile_id: str,
        device_id: str,
        justification: str = None,
        otp: str = None,
        ticket_id: str = None,
        ticket_type: str = None,
        headers: dict = None,
    ) -> dict:
        """
        Check out a device profile.

        This does not block on approval. If the profile requires approval use `request_approval()`, then check out
        again once the request has been approved.

        :param profile_id: The ID of the profile. Use `list()` to obtain the eligible profiles.
        :param device_id: The ID of the device. Use `list()` to obtain the eligible devices.
        :param justification: Optional justification for checking out the profile.
        :param otp: Optional time based one-time passcode used for step up authentication.
        :param ticket_id: Optional ITSM ticket ID.
        :param ticket_type: Optional ITSM ticket type or category.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :raises ApprovalRequiredButNoJustificationProvided: if the profile requires a justification or approval and no
            `justification` was given.
        :raises ProfileApprovalRequiredError: if the profile requires approval. Use `request_approval()`.
        :raises StepUpAuthRequiredButNotProvided: if the profile requires step up authentication and no `otp` was given.
        :raises StepUpAuthFailed: if the `otp` was rejected.
        :return: Details of the device checkout.
        """

        data = {}
        if justification:
            data['justification'] = justification
        if ticket_type:
            data['ticketType'] = ticket_type
        if ticket_id:
            data['ticketId'] = ticket_id

        if otp:
            response = self.britive.security.step_up_auth.authenticate(otp=otp)
            if response.get('result') == 'FAILED':
                raise StepUpAuthFailed

        try:
            return self.britive.post(f'{self.base_url}/{profile_id}/devices/{device_id}', json=data, headers=headers)
        except StepUpAuthenticationRequiredError as e:
            raise StepUpAuthRequiredButNotProvided(e) from e
        except (ApprovalJustificationRequiredError, ProfileApprovalRequiredError) as e:
            if not justification:
                raise ApprovalRequiredButNoJustificationProvided(e) from e
            raise

    def checkin(self, transaction_id: str, headers: dict = None) -> dict:
        """
        Check in a checked out device profile.

        :param transaction_id: The ID of the transaction.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: Details of the checked in device.
        """

        return self.britive.put(f'{self.base_url}/devices/{transaction_id}', headers=headers)

    def request_approval(
        self,
        profile_id: str,
        device_id: str,
        justification: str,
        ticket_id: str = None,
        ticket_type: str = None,
        headers: dict = None,
    ) -> dict:
        """
        Request approval to check out a device profile. Does not wait for the request to be dispositioned.

        :param profile_id: The ID of the profile.
        :param device_id: The ID of the device.
        :param justification: Justification for the request.
        :param ticket_id: Optional ITSM ticket ID.
        :param ticket_type: Optional ITSM ticket type or category.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :raises ProfileCheckoutAlreadyApproved: if the checkout is already approved.
        :return: Details of the approval request, including `requestId`.
        """

        data = {'justification': justification}
        if ticket_id and ticket_type:
            data.update(ticketId=ticket_id, ticketType=ticket_type)

        request = self.britive.post(
            f'{self.base_url}/{profile_id}/devices/{device_id}/approvalRequest', json=data, headers=headers
        )
        if request is None:
            raise ProfileCheckoutAlreadyApproved
        return request

    def withdraw_approval_request(self, profile_id: str, device_id: str, headers: dict = None) -> None:
        """
        Withdraw a pending approval request for a device profile.

        :param profile_id: The ID of the profile.
        :param device_id: The ID of the device.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: None
        """

        return self.britive.delete(
            f'{self.britive.base_url}/v1/approvals/consumer/papservice/resource',
            params={'resourceId': f'{profile_id}/{device_id}'},
            headers=headers,
        )
