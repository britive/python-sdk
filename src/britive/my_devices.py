from .exceptions import (
    ApprovalRequiredButNoJustificationProvided,
    ProfileCheckoutAlreadyApproved,
    StepUpAuthFailed,
    StepUpAuthRequiredButNotProvided,
)
from .exceptions.badrequest import ApprovalJustificationRequiredError, ProfileApprovalRequiredError
from .exceptions.generic import StepUpAuthenticationRequiredError


class MyDevices:
    """Self-service operations for the My Devices page.

    Methods return devices and allow actions available to the authenticated identity, without requiring
    administrative access. Checking out a device profile runs its grant scripts on the device.
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
        """List the device profiles the user has access to.

        :param filter_text: Filter the results.
        :param search_text: Search the results.
        :param page: Optional zero-based page number; omitted values use the API's paging defaults.
        :param size: Optional number of results per page.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: Dict with a `data` list and paging details. Returns one API page without auto-pagination.
        """
        params = {'filter': filter_text, 'searchText': search_text, 'page': page, 'size': size}
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
        """Check out a device profile, running its grant scripts on the device.

        This does not wait for approval. If approval is required, use `request_approval()` and check out again
        after approval. Checking in runs the corresponding revoke scripts.

        :param profile_id: The ID of the profile, available from `list()`.
        :param device_id: The ID of the device, available from `list()`.
        :param justification: Optional justification for the checkout.
        :param otp: Optional TOTP for step-up authentication.
        :param ticket_id: Optional ITSM ticket ID.
        :param ticket_type: Optional ITSM ticket type or category.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: Details of the device checkout.
        :raises ApprovalRequiredButNoJustificationProvided: If justification is required but not supplied.
        :raises ProfileApprovalRequiredError: If approval is required. Use `request_approval()`.
        :raises StepUpAuthRequiredButNotProvided: If step-up authentication is required.
        :raises StepUpAuthFailed: If the OTP is rejected.
        """
        data = {}
        if justification:
            data['justification'] = justification
        if ticket_type:
            data['ticketType'] = ticket_type
        if ticket_id:
            data['ticketId'] = ticket_id

        if otp:
            response = self.britive.security.step_up_auth.authenticate(otp=otp, headers=headers)
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
        """Check in a device profile, running its revoke scripts on the device.

        :param transaction_id: The checkout transaction ID.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: Details of the device check-in.
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
        """Request approval for a device profile without waiting for a decision.

        :param profile_id: The ID of the profile.
        :param device_id: The ID of the device.
        :param justification: Justification for the request.
        :param ticket_id: Optional ITSM ticket ID, supplied with `ticket_type`.
        :param ticket_type: Optional ITSM ticket type, supplied with `ticket_id`.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: Approval request details, including `requestId`.
        :raises ProfileCheckoutAlreadyApproved: If the checkout is already approved.
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
        """Withdraw a pending approval request for a device profile.

        :param profile_id: The ID of the profile.
        :param device_id: The ID of the device.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: None.
        """
        return self.britive.delete(
            f'{self.britive.base_url}/v1/approvals/consumer/papservice/resource',
            params={'resourceId': f'{profile_id}/{device_id}'},
            headers=headers,
        )
