import sys
import time
from typing import Callable
from . import exceptions

approval_exceptions = {
    'rejected': exceptions.ProfileApprovalRejected(),
    'cancelled': exceptions.ProfileApprovalWithdrawn(),
    'timeout': exceptions.ProfileApprovalTimedOut(),
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

    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/my-resources'

    def list_profiles(self, list_type: str = None, search_text: str = None) -> list:
        """
        List the profiles for which the user has access.

        :return: List of profiles.
        """

        params = {}
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

    def get_checked_out_profile(self, transaction_id: str) -> dict:
        """
        Retrieve details of a given checked out profile.

        :param transaction_id: The ID of the transaction.
        :return: Details of the given profile/transaction.
        """

        for t in self.list_checked_out_profiles():
            if t['transactionId'] == transaction_id:
                return t
        raise exceptions.TransactionNotFound()

    def _checkout(
        self,
        profile_id: str,
        resource_id: str,
        include_credentials: bool = False,
        justification: str = None,
        otp: str = None,
        wait_time: int = 60,
        max_wait_time: int = 600,
        progress_func: Callable = None
    ) -> dict:

        data = {'justification': justification}

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
                response = self.britive.step_up.authenticate(otp=otp)
                if response.get('result') == 'FAILED':
                    raise exceptions.StepUpAuthFailed()

            try:
                transaction = self.britive.post(
                    f'{self.base_url}/profiles/{profile_id}/resources/{resource_id}/checkout', json=data
                )
            except exceptions.ForbiddenRequest as e:
                if 'PE-0028' in str(e):  # Check for stepup totp
                    raise exceptions.StepUpAuthRequiredButNotProvided()
            # except exceptions.InvalidRequest as e:
            #     if 'MA-0010' in str(e):  # new approval process that de-couples approval from checkout
            #         # if the caller has not provided a justification we know for sure the call will fail
            #         # so raise the exception
            #         if not justification:
            #             raise exceptions.ApprovalRequiredButNoJustificationProvided()
            #
            #         # request approval
            #         status = self.request_approval(
            #             profile_id=profile_id,
            #             environment_id=environment_id,
            #             justification=justification,
            #             wait_time=wait_time,
            #             max_wait_time=max_wait_time,
            #             block_until_disposition=True,
            #             progress_func=progress_func,
            #         )
            #
            #         # handle the response based on the value of status
            #         if status == 'approved':
            #             transaction = self.britive.post(
            #                 f'{self.base_url}/{profile_id}/environments/{environment_id}', params=params, json=data
            #             )
            #         else:
            #             raise approval_exceptions[status]
                raise e

        transaction_id = transaction['transactionId']

        # inject credentials if asked
        if include_credentials:
            # if the transaction is not in status of checkedOut here it will be after the
            # return of this call and we update the transaction object accordingly
            credentials, transaction = self.credentials(
                transaction_id=transaction_id,
                transaction=transaction,
                return_transaction_details=True,
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
        otp: str = None,
        wait_time: int = 60,
        max_wait_time: int = 600,
        progress_func: Callable = None,
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
        :param otp: Optional time based one-time passcode use for step up authentication.
        :param wait_time: The number of seconds to sleep/wait between polling to check if the profile checkout
            was approved.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
        :return: Details about the checked out profile, and optionally the credentials generated by the checkout.
        :raises ApprovalRequiredButNoJustificationProvided: if approval is required but no justification is provided.
        :raises ApprovalWorkflowTimedOut: if max_wait_time has been reached while waiting for approval.
        :raises ApprovalWorkflowRejected: if the request to check out the profile was rejected.
        :raises ProfileApprovalTimedOut: if the approval request timed out exceeded the max time as specified by the
            profile policy.
        :raises ProfileApprovalRejected: if the approval request was rejected by the approver.
        :raises ProfileApprovalWithdrawn: if the approval request was withdrawn by the requester.
        """

        return self._checkout(
            profile_id=profile_id,
            resource_id=resource_id,
            include_credentials=include_credentials,
            justification=justification,
            wait_time=wait_time,
            max_wait_time=max_wait_time,
            progress_func=progress_func,
            otp=otp,
        )

    def checkout_by_name(
        self,
        profile_name: str,
        resource_name: str,
        include_credentials: bool = False,
        justification: str = None,
        otp: str = None,
        wait_time: int = 60,
        max_wait_time: int = 600,
        progress_func: Callable = None,
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
        :param otp: Optional time based one-time passcode use for step up authentication.
        :param wait_time: The number of seconds to sleep/wait between polling to check if the profile checkout
            was approved.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
        :return: Details about the checked out profile, and optionally the credentials generated by the checkout.
        :raises ApprovalRequiredButNoJustificationProvided: if approval is required but no justification is provided.
        :raises ApprovalWorkflowTimedOut: if max_wait_time has been reached while waiting for approval.
        :raises ApprovalWorkflowRejected: if the request to check out the profile was rejected.
        """

        ids = self._get_profile_and_resource_ids_given_names(profile_name, resource_name)

        return self._checkout(
            profile_id=ids['profile_id'],
            resource_id=ids['resource_id'],
            include_credentials=include_credentials,
            justification=justification,
            otp=otp,
            wait_time=wait_time,
            max_wait_time=max_wait_time,
            progress_func=progress_func,
        )

    def credentials(
        self,
        transaction_id: str,
        transaction: dict = None,
        return_transaction_details: bool = False,
        progress_func: Callable = None,
    ) -> any:
        """
        Return credentials of a checked out profile given the transaction ID.

        :param transaction_id: The ID of the transaction.
        :param transaction: Optional - the details of the transaction. Primary use is for internal purposes.
        :param return_transaction_details: Optional - whether to return the details of the transaction. Primary use is
            for internal purposes.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
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
        creds = self.britive.post(f'{self.base_url}/{transaction_id}/credentials')

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

    def _get_profile_and_resource_ids_given_names(self, profile_name: str, resource_name: str) -> dict:
        resource_profile_map = {
            f'{item["resourceName"].lower()}|{item["profileName"].lower()}': {
                'profile_id': item['profileId'],
                'resource_id': item['resourceId']
            }
            for item in self.list_profiles()
        }

        item = resource_profile_map.get(f'{resource_name.lower()}|{profile_name.lower()}')

        # do some error checking
        if not item:
            raise ValueError(f'resource and profile combination not found')

        return item
