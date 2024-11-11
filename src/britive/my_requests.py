import sys
import time
from typing import Any, Callable

from .exceptions import (
    ProfileApprovalMaxBlockTimeExceeded,
    ProfileCheckoutAlreadyApproved,
)


class MyRequests:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/approvals'

    def list(self) -> list:
        """
        List My Requests

        :return: List of My Requests.
        """

        return self.britive.get(self.britive.base_url, params={'requestType': 'myRequests'})

    def request_approval_by_name(
        self,
        profile_name: str,
        environment_name: str,
        justification: str,
        application_name: str = None,
        block_until_disposition: bool = False,
        max_wait_time: int = 600,
        progress_func: Callable = None,
        ticket_id: str = None,
        ticket_type: str = None,
        wait_time: int = 60,
    ) -> Any:
        """
        Requests approval to checkout a profile at a later time, using names of entities instead of IDs.

        Console vs. Programmatic access is not applicable here. The request for approval will allow the caller
        to checkout either type of access once the request has been approved.

        :param profile_name: The name of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param environment_name: The name of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param application_name: Optionally the name of the application, which can help disambiguate between profiles
            with the same name across applications.
        :param justification: Justification for checking out a profile that requires approval.
        :param block_until_disposition: Should this method wait/block until the request has been either approved,
            rejected, or withdrawn. If `True` then `wait_time` and `max_wait_time` will govern how long to wait before
            exiting.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception. Only applicable if `block_until_disposition = True`.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
        :param ticket_id: Optional ITSM ticket ID
        :param ticket_type: Optional ITSM ticket type or category
        :param wait_time: The number of seconds to sleep/wait between polling to check if the profile checkout
            was approved. Only applicable if `block_until_disposition = True`.
        :return: If `block_until_disposition = True` then returns the final status of the request. If
            `block_until_disposition = False` then returns details about the approval request.
        :raises ProfileApprovalMaxBlockTimeExceeded: if max_wait_time has been reached while waiting for approval.
        """

        ids = self._get_profile_and_environment_ids_given_names(profile_name, environment_name, application_name)

        return self.request_approval(
            profile_id=ids['profile_id'],
            environment_id=ids['environment_id'],
            justification=justification,
            block_until_disposition=block_until_disposition,
            max_wait_time=max_wait_time,
            progress_func=progress_func,
            ticket_id=ticket_id,
            ticket_type=ticket_type,
            wait_time=wait_time,
        )

    def request_approval(
        self,
        profile_id: str,
        environment_id: str,
        justification: str,
        block_until_disposition: bool = False,
        max_wait_time: int = 600,
        progress_func: Callable = None,
        ticket_id: str = None,
        ticket_type: str = None,
        wait_time: int = 60,
    ) -> Any:
        """
        Requests approval to checkout a profile at a later time.

        Console vs. Programmatic access is not applicable here. The request for approval will allow the caller
        to checkout either type of access once the request has been approved.

        :param profile_id: The ID of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param environment_id: The ID of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param justification: Justification for checking out a profile that requires approval.
        :param block_until_disposition: Should this method wait/block until the request has been either approved,
            rejected, or withdrawn. If `True` then `wait_time` and `max_wait_time` will govern how long to wait before
            exiting.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception. Only applicable if `block_until_disposition = True`.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
        :param ticket_id: Optional ITSM ticket ID
        :param ticket_type: Optional ITSM ticket type or category
        :param wait_time: The number of seconds to sleep/wait between polling to check if the profile checkout
            was approved. Only applicable if `block_until_disposition = True`.
        :return: If `block_until_disposition = True` then returns the final status of the request. If
            `block_until_disposition = False` then returns details about the approval request.
        :raises ProfileApprovalMaxBlockTimeExceeded: if max_wait_time has been reached while waiting for approval.
        """

        data = {'justification': justification}

        if ticket_id and ticket_type:
            data.update(ticketId=ticket_id, ticketType=ticket_type)

        request = self.britive.post(
            f'{self.britive.base_url}/access/{profile_id}/environments/{environment_id}/approvalRequest', json=data
        )

        if request is None:
            raise ProfileCheckoutAlreadyApproved()

        request_id = request['requestId']

        if block_until_disposition:
            try:
                quit_time = time.time() + max_wait_time
                while True:
                    status = self.approval_request_status(request_id=request_id)['status'].lower()
                    if status == 'pending':
                        if time.time() >= quit_time:
                            raise ProfileApprovalMaxBlockTimeExceeded()
                        if progress_func:
                            progress_func('awaiting approval')
                        time.sleep(wait_time)
                        continue
                    # status == timeout or approved or rejected or cancelled
                    return status
            except KeyboardInterrupt:  # handle Ctrl+C (^C)
                # the first ^C we get we will try to withdraw the request
                # if we get another ^C while doing this we simply exit immediately
                try:
                    time.sleep(1)  # give the caller a small window to ^C again
                    self.withdraw_approval_request(request_id=request_id)
                    sys.exit()
                except KeyboardInterrupt:
                    sys.exit()

        else:
            return request

    def approval_request_status(self, request_id: str) -> dict:
        """
        Provides details on and approval request.

        :param request_id: The ID of the approval request.
        :return: Details of the approval request.
        """

        return self.britive.get(f'{self.britive.base_url}/{request_id}')

    def withdraw_approval_request_by_name(
        self, profile_name: str, environment_name: str, application_name: str = None
    ) -> None:
        """
        Withdraws a pending approval request, using names of entities instead of IDs.

        :param profile_name: The name of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param environment_name: The name of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param application_name: Optionally the name of the application, which can help disambiguate between profiles
            with the same name across applications.
        :return: None
        """

        ids = self._get_profile_and_environment_ids_given_names(profile_name, environment_name, application_name)

        return self.withdraw_approval_request(profile_id=ids['profile_id'], environment_id=ids['environment_id'])

    def withdraw_approval_request(
        self, request_id: str = None, profile_id: str = None, environment_id: str = None
    ) -> None:
        """
        Withdraws a pending approval request.

        Either `request_id` or (`profile_id` AND `environment_id`) are required.

        :param request_id: The ID of the approval request.
        :param profile_id: The ID of the profile.
        :param environment_id: The ID of the environment.
        :return: None
        """

        url = None
        if request_id:
            url = f'{self.britive.base_url}/{request_id}'
        else:
            if not profile_id:
                raise ValueError('profile_id is required.')
            if not environment_id:
                raise ValueError('environment_id is required')
            url = f'{self.britive.base_url}/consumer/papservice/resource?resourceId=' f'{profile_id}/{environment_id}'

        return self.britive.delete(url)
