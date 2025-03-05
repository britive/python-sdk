import time
from typing import Any, Callable

from .exceptions import (
    ApprovalRequiredButNoJustificationProvided,
    ProfileApprovalRejected,
    ProfileApprovalTimedOut,
    ProfileApprovalWithdrawn,
    StepUpAuthFailed,
    StepUpAuthRequiredButNotProvided,
    TransactionNotFound,
)
from .exceptions.badrequest import ApprovalJustificationRequiredError, ProfileApprovalRequiredError
from .exceptions.generic import StepUpAuthenticationRequiredError
from .helpers import HelperMethods
from .my_requests import MyResourcesRequests

approval_exceptions = {
    'rejected': ProfileApprovalRejected(),
    'cancelled': ProfileApprovalWithdrawn(),
    'timeout': ProfileApprovalTimedOut(),
    'withdrawn': ProfileApprovalWithdrawn(),
}


class MyResources:
    """
    This class is meant to be called by end users. It is an API layer on top of the actions that can be performed on the
    "My Resources" page of the Britive UI.

    No "administrative" access is required by the methods in this class. Each method will only return resources/allow
    actions which are permitted to be performed by the user/service identity, as identified by an API token or
    interactive login bearer token.

    It is entirely possible that an administrator who makes these API calls could get nothing returned, as that
    administrator may not have access to any resource profiles.
    """

    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/my-resources'
        self._get_profile_and_resource_ids_given_names = HelperMethods(
            self.britive
        ).get_profile_and_resource_ids_given_names

        # MyRequests
        __my_requests = MyResourcesRequests(self.britive)
        self.request_approval = __my_requests.request_approval
        self.request_approval_by_name = __my_requests.request_approval_by_name
        self.withdraw_approval_request = __my_requests.withdraw_approval_request
        self.withdraw_approval_request_by_name = __my_requests.withdraw_approval_request_by_name

    # Let's just mimic my_access.list functionality for now.
    def list(self, filter_text: str = None, list_type: str = None, search_text: str = None, size: int = None) -> dict:
        """
        List the resource details for the current user.

        :param filter_text: filter resource by key, e.g. `filter_text='key eq env'`
        :param list_type: filter resources by type, e.g. `list_type='frequently-used'`
        :param search_text: filter resources by search text.
        :param size: reduce the size of the response to the specified limit.
        :return: Dict of resource details.
        """

        params = {}
        if filter_text:
            params['filter'] = filter_text
        if list_type:
            params['type'] = list_type
        if search_text:
            params['searchText'] = search_text
        if size:
            params.update(page=0, size=size)

        return self.britive.get(self.base_url, params=params)

    def list_profiles(self, filter_text: str = None, list_type: str = None, search_text: str = None) -> list:
        """
        List the profiles for which the user has access.

        :param filter_text: filter resource by key, e.g. `filter_text='key eq env'`
        :param list_type: filter resources by type, e.g. `list_type='frequently-used'`
        :param search_text: filter resources by search text.
        :return: List of profiles.
        """

        params = {}
        if filter_text:
            params['filter'] = filter_text
        if list_type:
            params['type'] = list_type
        if search_text:
            params['searchText'] = search_text

        return self.britive.get(self.base_url, params=params)

    def search(self, search_text: str) -> list:
        """
        Search the list of resources/profiles for which the user has access.

        :param search_text: The text to search.
        :return: List of profiles.
        """

        return self.list_profiles(search_text=search_text)

    def list_checked_out_profiles(self) -> list:
        """
        Return list of details on currently checked out profiles for the user.

        :return: List of checked out profiles.
        """

        return [i for i in self.list_profiles() if i['transactionId']]

    def list_response_templates(self, transaction_id: str) -> list:
        """
        List the Response Templates for a checked out profile.

        :param transaction_id: Transaction ID of the checked out profile.
        :return: List of response templates.
        """

        return self.britive.get(f'{self.base_url}/{transaction_id}/templates')

    def get_checked_out_profile(self, transaction_id: str) -> dict:
        """
        Retrieve details of a given checked out profile.

        :param transaction_id: The ID of the transaction.
        :return: Details of the given profile/transaction.
        """

        for t in self.list_checked_out_profiles():
            if t['transactionId'] == transaction_id:
                return t
        raise TransactionNotFound

    def _checkout(
        self,
        profile_id: str,
        resource_id: str,
        include_credentials: bool = False,
        justification: str = None,
        max_wait_time: int = 600,
        otp: str = None,
        progress_func: Callable = None,
        response_template: str = None,
        ticket_id: str = None,
        ticket_type: str = None,
        wait_time: int = 60,
    ) -> dict:
        data = {}
        if justification:
            data['justification'] = justification
        if ticket_type:
            data['ticketType'] = ticket_type
        if ticket_id:
            data['ticketId'] = ticket_id

        transaction = None

        # let's see if there is already a checked out profile
        progress_pending_checked_out_profiles_sent = False
        while True:  # will break the loop when needed
            loop = False
            if progress_func and not progress_pending_checked_out_profiles_sent:
                progress_func('reviewing currently checked out profiles')
                progress_pending_checked_out_profiles_sent = True
            for p in self.list_checked_out_profiles():
                right_profile = p['profileId'] == profile_id
                right_resource = p['resourceId'] == resource_id
                if all([right_profile, right_resource]):
                    if p['checkedInTime'] is None:  # still currently checked out so we can move on
                        transaction = p
                        break
                    # we are in the middle of a profile being checked in so cannot check it out yet
                    loop = True
            if loop:
                if progress_func:
                    progress_func('pending profile checkin')
                time.sleep(1)
            else:
                break

        # if not check it out
        if not transaction:
            if otp:
                response = self.britive.security.step_up_auth.authenticate(otp=otp)
                if response.get('result') == 'FAILED':
                    raise StepUpAuthFailed

            try:
                transaction = self.britive.post(
                    f'{self.base_url}/profiles/{profile_id}/resources/{resource_id}/checkout', json=data
                )
            except StepUpAuthenticationRequiredError as e:
                raise StepUpAuthRequiredButNotProvided(e) from e
            except (ApprovalJustificationRequiredError, ProfileApprovalRequiredError) as e:
                if not justification:
                    raise ApprovalRequiredButNoJustificationProvided from e

                # request approval
                status = self.request_approval(
                    block_until_disposition=True,
                    justification=justification,
                    max_wait_time=max_wait_time,
                    profile_id=profile_id,
                    progress_func=progress_func,
                    resource_id=resource_id,
                    ticket_id=ticket_id,
                    ticket_type=ticket_type,
                    wait_time=wait_time,
                )

                # handle the response based on the value of status
                if status == 'approved':
                    transaction = self.britive.post(
                        f'{self.base_url}/profiles/{profile_id}/resources/{resource_id}/checkout', json=data
                    )
                else:
                    raise approval_exceptions[status](e) from e
                raise e

        transaction_id = transaction['transactionId']

        # inject credentials if asked
        if include_credentials:
            # if the transaction is not in status of checkedOut here it will be after the
            # return of this call and we update the transaction object accordingly
            credentials, transaction = self.credentials(
                response_template=response_template,
                return_transaction_details=True,
                transaction_id=transaction_id,
                transaction=transaction,
                progress_func=progress_func,
            )
            transaction['credentials'] = credentials

        if progress_func:
            progress_func('complete')
        return transaction

    def checkout(
        self,
        profile_id: str,
        resource_id: str,
        include_credentials: bool = False,
        justification: str = None,
        max_wait_time: int = 600,
        otp: str = None,
        progress_func: Callable = None,
        response_template: str = None,
        ticket_id: str = None,
        ticket_type: str = None,
        wait_time: int = 60,
    ) -> dict:
        """
        Checkout a profile.

        If the profile has already been checked out this method will return the details of the checked out profile.

        If approval is required, this method will continue to check if approval has been obtained. Once the request
        is approved the profile will be checked out. Sending a `SIGINT/KeyboardInterrupt/Ctrl+C/^C` while waiting for
        the approval request to be dispositioned will withdraw the request. Sending a second `^C` immediately after
        the first will immediately exit the program.

        :param profile_id: The ID of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param resource_id: The ID of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param include_credentials: True if tokens should be included in the response. False if the caller wishes to
            call `credentials()` at a later time. If True, the `credentials` key will be included in the response which
            contains the response from `credentials()`. Setting this parameter to `True` will result in a synchronous
            call vs. setting to `False` will allow for an async call.
        :param justification: Optional justification if checking out the profile requires approval.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception.
        :param otp: Optional time based one-time passcode use for step up authentication.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
        :param response_template: Optional response template to use in conjunction with `include_credentials`.
        :param ticket_id: Optional ITSM ticket ID
        :param ticket_type: Optional ITSM ticket type or category
        :param wait_time: The number of seconds to sleep/wait between polling to check if the profile checkout
            was approved.
        :return: Details about the checked out profile, and optionally the credentials generated by the checkout.
        :raises ApprovalRequiredButNoJustificationProvided: if approval is required but no justification is provided.
        :raises ProfileApprovalRejected: if the approval request was rejected by the approver.
        :raises ProfileApprovalTimedOut: if the approval request timed out exceeded the max time as specified by the
            profile policy.
        :raises ProfileApprovalWithdrawn: if the approval request was withdrawn by the requester.
        """

        return self._checkout(
            profile_id=profile_id,
            resource_id=resource_id,
            include_credentials=include_credentials,
            justification=justification,
            max_wait_time=max_wait_time,
            otp=otp,
            progress_func=progress_func,
            response_template=response_template,
            ticket_id=ticket_id,
            ticket_type=ticket_type,
            wait_time=wait_time,
        )

    def checkout_by_name(
        self,
        profile_name: str,
        resource_name: str,
        include_credentials: bool = False,
        justification: str = None,
        max_wait_time: int = 600,
        otp: str = None,
        progress_func: Callable = None,
        response_template: str = None,
        ticket_id: str = None,
        ticket_type: str = None,
        wait_time: int = 60,
    ) -> dict:
        """
        Checkout a profile by supplying the names of entities vs. the IDs of those entities.

        If approval is required, this method will continue to check if approval has been obtained. Once the request
        is approved the profile will be checked out. Sending a `SIGINT/KeyboardInterrupt/Ctrl+C/^C` while waiting for
        the approval request to be dispositioned will withdraw the request. Sending a second `^C` immediately after
        the first will immediately exit the program.

        :param profile_name: The name of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param resource_name: The name of the resource. Use `list_profiles()` to obtain the eligible rsources.
        :param include_credentials: True if tokens should be included in the response. False if the caller wishes to
            call `credentials()` at a later time. If True, the `credentials` key will be included in the response which
            contains the response from `credentials()`. Setting this parameter to `True` will result in a synchronous
            call vs. setting to `False` will allow for an async call.
        :param justification: Optional justification if checking out the profile requires approval.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception.
        :param otp: Optional time based one-time passcode use for step up authentication.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
        :param response_template: Optional response template to use in conjunction with `include_credentials`.
        :param ticket_id: Optional ITSM ticket ID
        :param ticket_type: Optional ITSM ticket type or category
        :param wait_time: The number of seconds to sleep/wait between polling to check if the profile checkout
            was approved.
        :return: Details about the checked out profile, and optionally the credentials generated by the checkout.
        :raises ApprovalRequiredButNoJustificationProvided: if approval is required but no justification is provided.
        :raises ProfileApprovalRejected: if the approval request was rejected by the approver.
        :raises ProfileApprovalTimedOut: if the approval request timed out exceeded the max time as specified by the
            profile policy.
        :raises ProfileApprovalWithdrawn: if the approval request was withdrawn by the requester.
        """

        ids = self._get_profile_and_resource_ids_given_names(profile_name, resource_name)

        return self._checkout(
            profile_id=ids['profile_id'],
            resource_id=ids['resource_id'],
            include_credentials=include_credentials,
            justification=justification,
            max_wait_time=max_wait_time,
            otp=otp,
            progress_func=progress_func,
            response_template=response_template,
            ticket_id=ticket_id,
            ticket_type=ticket_type,
            wait_time=wait_time,
        )

    def credentials(
        self,
        transaction_id: str,
        progress_func: Callable = None,
        response_template: str = None,
        return_transaction_details: bool = False,
        transaction: dict = None,
    ) -> Any:
        """
        Return credentials of a checked out profile given the transaction ID.

        :param transaction_id: The ID of the transaction.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
        :param response_template: Optional - return the string value of a given response template.
        :param return_transaction_details: Optional - whether to return the details of the transaction. Primary use is
            for internal purposes.
        :param transaction: Optional - the details of the transaction. Primary use is for internal purposes.
        :return: Credentials associated with the checked out profile represented by the specified transaction.
        """

        # step 1: get the details of the transaction so we can make the appropriate API call
        # we only need to get the details of the transaction if they are not already provided
        # or the transaction is not in the state of checkedOut
        if not transaction or transaction['status'] != 'checkedOut':
            while True:
                transaction = self.get_checked_out_profile(transaction_id=transaction_id)
                if transaction['status'] == 'checkOutSubmitted':  # async checkout process
                    if progress_func:
                        progress_func('credential creation')
                    time.sleep(1)
                    continue
                # status == checkedOut
                break

        # step 2: make the proper API call
        creds = self.britive.post(
            f'{self.base_url}/{transaction_id}/credentials',
            params={'templateName': response_template} if response_template else {},
        )

        if return_transaction_details:
            return creds, transaction
        return creds

    def checkin(self, transaction_id: str) -> dict:
        """
        Check in a checked out profile.

        :param transaction_id: The ID of the transaction.
        :return: Details of the checked in profile.
        """

        return self.britive.post(f'{self.base_url}/{transaction_id}/check-in')

    def checkin_by_name(self, profile_name: str, resource_name: str) -> dict:
        """
        Check in a checked out profile by supplying the names of entities vs. the IDs of those entities

        :param profile_name: The name of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param resource_name: The name of the environment. Use `list_profiles()` to obtain the eligible resources.
        :return: Details of the checked in profile.
        """

        ids = self._get_profile_and_resource_ids_given_names(profile_name, resource_name)

        transaction_id = None
        for profile in self.list_checked_out_profiles():
            if profile['resourceId'] == ids['resource_id'] and profile['profileId'] == ids['profile_id']:
                transaction_id = profile['transactionId']
                break
        if not transaction_id:
            raise ValueError('no checked out profile found for the given profile_name and resource_name')

        return self.checkin(transaction_id=transaction_id)

    def frequents(self) -> list:
        """
        Return list of frequently used profiles for the user.

        :return: List of profiles.
        """

        return self.list_profiles(list_type='frequently-used')

    def favorites(self) -> list:
        """
        Return list of favorite profiles for the user.

        :return: List of profiles.
        """

        return self.list_profiles(list_type='favorites')

    def add_favorite(self, resource_id: str, profile_id: str) -> dict:
        """
        Add a resource favorite.

        :param resource_id: The resource ID of the resource favorite to add.
        :param profile_id: The profile ID of the resource favorite to add.
        :return: Details of the favorite resource.
        """

        data = {'resource-id': resource_id, 'profile-id': profile_id}

        return self.post(f'{self.base_url}/favorites', json=data)

    def delete_favorite(self, favorite_id: str) -> None:
        """
        Delete a resource favorite.

        :param favorite_id: The ID of the resource favorite to delete.
        :return: None
        """

        return self.delete(f'{self.base_url}/favorites/{favorite_id}')

    def get_profile_settings(self, profile_id: str, resource_id: str) -> dict:
        """
        Retrieve settings of a profile.

        :param profile_id: The ID of the profile.
        :param resource_id: The ID of the resource.
        :return: Dict of the profile settings.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}/resources/{resource_id}/settings')

    def get_profile_settings_by_name(self, profile_name: str, resource_name: str) -> dict:
        """
        Retrieve settings of a profile by name.

        :param profile_name: The name of the profile.
        :param resource_name: The name of the resource.
        :return: Dict of the profile settings.
        """

        ids = self._get_profile_and_resource_ids_given_names(profile_name=profile_name, resource_name=resource_name)

        return self.get_profile_settings(profile_id=ids['profile_id'], resource_id=ids['resource_id'])
