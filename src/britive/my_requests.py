import time
from typing import Any, Callable

from .exceptions import (
    ProfileApprovalMaxBlockTimeExceeded,
    ProfileApprovalWithdrawn,
    ProfileCheckoutAlreadyApproved,
)
from .helpers import HelperMethods


class MyRequests:
    """
    This class is meant to be called by end users. It is an API layer on top of the actions that can be performed on the
    "My Requests" page of the Britive UI or when requesting approval for a profile checkout.

    No "administrative" access is required by the methods in this class. Each method will only return request/allow
    actions which are permitted to be performed by the user/service identity, as identified by an API token or
    interactive login bearer token.

    It is entirely possible that an administrator who makes these API calls could get nothing returned, as that
    administrator may not have any requests or profiles which require one.
    """

    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/approvals'
        self._helper = HelperMethods(self.britive)

    def list(self) -> list:
        """
        List My Requests

        :return: List of My Requests.
        """

        return self.britive.get(f'{self.base_url}/', params={'requestType': 'myRequests'})

    def approval_request_status(self, request_id: str) -> dict:
        """
        Get the details of an approval request.

        :param request_id: The ID of the approval request.
        :return: Details of the approval request.
        """

        return self.britive.get(f'{self.base_url}/{request_id}')

    def withdraw_approval_request(self, request_id: str) -> None:
        """
        Withdraws a pending approval request.

        :param request_id: The ID of the approval request.
        :return: None
        """

        return self._withdraw_approval_request(request_id=request_id)

    def _request_approval(
        self,
        profile_id: str,
        justification: str,
        entity_id: str,
        entity_type: str,
        block_until_disposition: bool = False,
        max_wait_time: int = 600,
        progress_func: Callable = None,
        ticket_id: str = None,
        ticket_type: str = None,
        wait_time: int = 60,
    ) -> Any:
        data = {'justification': justification}

        if ticket_id and ticket_type:
            data.update(ticketId=ticket_id, ticketType=ticket_type)

        url = (
            f'{self.britive.base_url}/access/{profile_id}/{entity_type}/{entity_id}/approvalRequest'
            if entity_type == 'environments'
            else (
                f'{self.britive.base_url}/resource-manager/my-resources/profiles/'
                f'{profile_id}/resources/{entity_id}/approvalRequest'
            )
        )
        request = self.britive.post(url, json=data)

        if request is None:
            raise ProfileCheckoutAlreadyApproved

        request_id = request['requestId']

        if block_until_disposition:
            try:
                quit_time = time.time() + max_wait_time
                while time.time() <= quit_time:
                    status = self.approval_request_status(request_id=request_id)['status'].lower()
                    if status == 'pending':
                        if progress_func:
                            progress_func('awaiting approval')
                        time.sleep(wait_time)
                        continue
                    # status == timeout or approved or rejected or cancelled
                    return status
                raise ProfileApprovalMaxBlockTimeExceeded
            except KeyboardInterrupt as e:  # handle Ctrl+C (^C)
                try:
                    # the first ^C we get we will try to withdraw the request
                    time.sleep(1)  # give the caller a small window to ^C again
                    self._withdraw_approval_request(request_id=request_id)
                    raise ProfileApprovalWithdrawn('user interrupt.') from e
                except KeyboardInterrupt:
                    raise e from None
        else:
            return request

    def _request_approval_by_name(
        self,
        justification: str,
        profile_name: str,
        entity_name: str,
        entity_type: str,
        application_name: str = None,
        block_until_disposition: bool = False,
        max_wait_time: int = 600,
        progress_func: Callable = None,
        ticket_id: str = None,
        ticket_type: str = None,
        wait_time: int = 60,
    ) -> Any:
        if entity_type == 'environments':
            ids = self._helper.get_profile_and_environment_ids_given_names(profile_name, entity_name, application_name)
            return self._request_approval(
                profile_id=ids['profile_id'],
                justification=justification,
                entity_id=ids['environment_id'],
                entity_type=entity_type,
                block_until_disposition=block_until_disposition,
                max_wait_time=max_wait_time,
                progress_func=progress_func,
                ticket_id=ticket_id,
                ticket_type=ticket_type,
                wait_time=wait_time,
            )
        ids = self._helper.get_profile_and_resource_ids_given_names(profile_name, entity_name)
        return self._request_approval(
            profile_id=ids['profile_id'],
            justification=justification,
            entity_id=ids['resource_id'],
            entity_type=entity_type,
            block_until_disposition=block_until_disposition,
            max_wait_time=max_wait_time,
            progress_func=progress_func,
            ticket_id=ticket_id,
            ticket_type=ticket_type,
            wait_time=wait_time,
        )

    def _withdraw_approval_request(
        self, request_id: str = None, profile_id: str = None, entity_id: str = None, entity_type: str = None
    ) -> None:
        url = request_id if request_id else f'consumer/{entity_type}/resource?resourceId={profile_id}/{entity_id}'

        return self.britive.delete(f'{self.base_url}/{url}')


class MyAccessRequests(MyRequests):
    def request_approval_by_name(
        self,
        environment_name: str,
        justification: str,
        profile_name: str,
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

        :param profile_name: The name of the profile.
            Use `my_access.list_profiles()` to obtain the eligible profiles.
        :param environment_name: The name of the environment.
            Use `my_access.list_profiles()` to obtain the eligible environments.
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

        return self._request_approval_by_name(
            entity_name=environment_name,
            justification=justification,
            profile_name=profile_name,
            application_name=application_name,
            block_until_disposition=block_until_disposition,
            entity_type='environments',
            max_wait_time=max_wait_time,
            progress_func=progress_func,
            ticket_id=ticket_id,
            ticket_type=ticket_type,
            wait_time=wait_time,
        )

    def request_approval(
        self,
        profile_id: str,
        justification: str,
        block_until_disposition: bool = False,
        environment_id: str = None,
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

        :param profile_id: The ID of the profile.
            Use `my_access.list_profiles()` to obtain the eligible profiles.
        :param environment_id: The ID of the environment.
            Use `my_access.list_profiles()` to obtain the eligible environments.
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

        return self._request_approval(
            justification=justification,
            profile_id=profile_id,
            entity_id=environment_id,
            entity_type='environments',
            block_until_disposition=block_until_disposition,
            max_wait_time=max_wait_time,
            progress_func=progress_func,
            ticket_id=ticket_id,
            ticket_type=ticket_type,
            wait_time=wait_time,
        )

    def withdraw_approval_request_by_name(
        self, profile_name: str, environment_name: str = None, application_name: str = None
    ) -> None:
        """
        Withdraws a pending approval request, using names of entities instead of IDs.

        :param profile_name: The name of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param environment_name: The name of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param application_name: Optionally the name of the application, which can help disambiguate between profiles
            with the same name across applications.
        :return: None
        """

        ids = self._helper.get_profile_and_environment_ids_given_names(profile_name, environment_name, application_name)

        return self._withdraw_approval_request(
            profile_id=ids['profile_id'], entity_id=ids['environment_id'], entity_type='papservice'
        )

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
        if not request_id and not all([profile_id, environment_id]):
            raise ValueError('profile_id and environment_id are required')

        return self._withdraw_approval_request(
            profile_id=profile_id, entity_id=environment_id, entity_type='papservice'
        )


class MyResourcesRequests(MyRequests):
    def request_approval(
        self,
        justification: str,
        profile_id: str,
        resource_id: str,
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

        :param justification: Justification for checking out a profile that requires approval.
        :param profile_id: The ID of the profile.
            Use `my_resources.list_profiles()` to obtain the eligible profiles.
        :param resource_id: The ID of the resource.
            Use `my_resources.list_profiles()` to obtain the eligible resources.
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

        return self._request_approval(
            justification=justification,
            profile_id=profile_id,
            entity_id=resource_id,
            entity_type='resource',
            block_until_disposition=block_until_disposition,
            max_wait_time=max_wait_time,
            progress_func=progress_func,
            ticket_id=ticket_id,
            ticket_type=ticket_type,
            wait_time=wait_time,
        )

    def request_approval_by_name(
        self,
        justification: str,
        profile_name: str,
        resource_name: str,
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

        :param justification: Justification for checking out a profile that requires approval.
        :param profile_name: The name of the profile.
            Use `my_resources.list_profiles()` to obtain the eligible profiles.
        :param resource_name: The name of the resource.
            Use `my_resources.list_profiles()` to obtain the eligible resources.
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

        return self._request_approval_by_name(
            justification=justification,
            profile_name=profile_name,
            entity_name=resource_name,
            entity_type='resource',
            block_until_disposition=block_until_disposition,
            max_wait_time=max_wait_time,
            progress_func=progress_func,
            ticket_id=ticket_id,
            ticket_type=ticket_type,
            wait_time=wait_time,
        )

    def withdraw_approval_request_by_name(self, profile_name: str, resource_name: str = None) -> None:
        """
        Withdraws a pending approval request, using names of entities instead of IDs.

        :param profile_name: The name of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param resource_name: The name of the resource. Use `list_profiles()` to obtain the eligible resources.
        :return: None
        """

        ids = self._helper.get_profile_and_resource_ids_given_names(profile_name, resource_name)

        return self._withdraw_approval_request(
            profile_id=ids['profile_id'], entity_id=ids['resource_id'], entity_type='resourceprofile'
        )

    def withdraw_approval_request(
        self, request_id: str = None, profile_id: str = None, resource_id: str = None
    ) -> None:
        """
        Withdraws a pending approval request.

        Either `request_id` or (`profile_id` AND `resource_id`) are required.

        :param request_id: The ID of the approval request.
        :param profile_id: The ID of the profile.
        :param resource_id: The ID of the resource.
        :return: None
        """

        if not request_id and not all([profile_id, resource_id]):
            raise ValueError('profile_id and resource_id are required')

        return self._withdraw_approval_request(
            profile_id=profile_id, entity_id=resource_id, entity_type='resourceprofile'
        )
