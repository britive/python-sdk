from . import exceptions
import time
from typing import Callable


approval_exceptions = {
    'rejected': exceptions.ProfileApprovalRejected(),
    'cancelled': exceptions.ProfileApprovalWithdrawn(),
    'timeout': exceptions.ProfileApprovalTimedOut()
}


class MyAccess:
    """
    This class is meant to be called by end users (as part of custom API integration work or the yet to be built
    Python based Britive CLI tooling). It is an API layer on top of the actions that can be performed on the
    "My Access" page of the Britive UI.
    
    No "administrative" access is required by the methods in this class. Each method will only return resources/allow
    actions which are permitted to be performed by the user/service identity, as identified by an API token or
    interactive login bearer token.

    It is entirely possible that an administrator who makes these API calls could get nothing returned, as that
    administrator may not have access to any profiles.
    """

    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/access'

    def list_profiles(self):
        """
        List the profiles for which the user has access.

        :return: List of profiles.
        """

        return self.britive.get(self.base_url)

    def list_checked_out_profiles(self) -> list:
        """
        Return list of details on currently checked out profiles for the user.

        :return: List of checked out profiles.
        """

        return self.britive.get(f'{self.base_url}/app-access-status')

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

    def request_approval_by_name(self, profile_name: str, environment_name: str, application_name: str = None,
                                 justification: str = None, wait_time: int = 60, max_wait_time: int = 600,
                                 block_until_disposition: bool = False, progress_func: Callable = None) -> any:
        """
        Requests approval to checkout a profile at a later time, using names of entities instead of IDs.

        Console vs. Programmatic access is not applicable here. The request for approval will allow the caller
        to checkout either type of access once the request has been approved.

        :param profile_name: The name of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param environment_name: The name of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param application_name: Optionally the name of the application, which can help disambiguate between profiles
            with the same name across applications.
        :param justification: Optional justification if checking out the profile requires approval.
        :param wait_time: The number of seconds to sleep/wait between polling to check if the profile checkout
            was approved. Only applicable if `block_until_disposition = True`.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception. Only applicable if `block_until_disposition = True`.
        :param block_until_disposition: Should this method wait/block until the request has been either approved,
            rejected, or withdrawn. If `True` then `wait_time` and `max_wait_time` will govern how long to wait before
            exiting.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
        :return: If `block_until_disposition = True` then returns the final status of the request. If
            `block_until_disposition = False` then returns details about the approval request.
        :raises ProfileApprovalMaxBlockTimeExceeded: if max_wait_time has been reached while waiting for approval.
        """

        ids = self._get_profile_and_environment_ids_given_names(profile_name, environment_name, application_name)

        return self.request_approval(
            profile_id=ids['profile_id'],
            environment_id=ids['environment_id'],
            justification=justification,
            wait_time=wait_time,
            max_wait_time=max_wait_time,
            block_until_disposition=block_until_disposition,
            progress_func=progress_func
        )

    def request_approval(self, profile_id: str, environment_id: str, justification: str, wait_time: int = 60,
                         max_wait_time: int = 600, block_until_disposition: bool = False,
                         progress_func: Callable = None) -> any:
        """
        Requests approval to checkout a profile at a later time, by supplying the names of entities vs. the IDs of
        those entities.

        Console vs. Programmatic access is not applicable here. The request for approval will allow the caller
        to checkout either type of access once the request has been approved.

        :param profile_id: The ID of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param environment_id: The ID of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param justification: Optional justification if checking out the profile requires approval.
        :param wait_time: The number of seconds to sleep/wait between polling to check if the profile checkout
            was approved. Only applicable if `block_until_disposition = True`.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception. Only applicable if `block_until_disposition = True`.
        :param block_until_disposition: Should this method wait/block until the request has been either approved,
            rejected, or withdrawn. If `True` then `wait_time` and `max_wait_time` will govern how long to wait before
            exiting.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
        :return: If `block_until_disposition = True` then returns the final status of the request. If
            `block_until_disposition = False` then returns details about the approval request.
        :raises ProfileApprovalMaxBlockTimeExceeded: if max_wait_time has been reached while waiting for approval.
        """

        data = {
            'justification': justification
        }

        request = self.britive.post(
            f'{self.base_url}/{profile_id}/environments/{environment_id}/approvalRequest',
            json=data
        )
        request_id = request['requestId']

        if block_until_disposition:
            try:
                quit_time = time.time() + max_wait_time
                while True:
                    status = self.approval_request_status(request_id=request_id)['status'].lower()
                    if status == 'pending':
                        if time.time() >= quit_time:
                            raise exceptions.ProfileApprovalMaxBlockTimeExceeded()
                        if progress_func:
                            progress_func('awaiting approval')
                        time.sleep(wait_time)
                        continue
                    else:  # status == timeout or approved or rejected or cancelled
                        return status
            except KeyboardInterrupt:  # handle Ctrl+C (^C)
                # the first ^C we get we will try to withdraw the request
                # if we get another ^C while doing this we simply exit immediately
                try:
                    time.sleep(1)  # give the caller a small window to ^C again
                    self.withdraw_approval_request(request_id=request_id)
                    exit()
                except KeyboardInterrupt:
                    exit()

        else:
            return request

    def approval_request_status(self, request_id: str) -> dict:
        """
        Provides details on and approval request.

        :param request_id: The ID of the approval request.
        :return: Details of the approval request.
        """

        return self.britive.get(f'{self.britive.base_url}/v1/approvals/{request_id}')

    def withdraw_approval_request_by_name(self, profile_name: str, environment_name: str,
                                          application_name: str = None) -> None:
        """
        Withdraws a pending approval request, using names of entities instead of IDs.

        :param profile_name: The name of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param environment_name: The name of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param application_name: Optionally the name of the application, which can help disambiguate between profiles
            with the same name across applications.
        :return: None
        """

        ids = self._get_profile_and_environment_ids_given_names(profile_name, environment_name, application_name)

        return self.withdraw_approval_request(
            profile_id=ids['profile_id'],
            environment_id=ids['environment_id']
        )

    def withdraw_approval_request(self, request_id: str = None, profile_id: str = None,
                                  environment_id: str = None) -> None:
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
            url = f'{self.britive.base_url}/v1/approvals/{request_id}'
        else:
            if not profile_id:
                raise ValueError('profile_id is required.')
            if not environment_id:
                raise ValueError('environment_id is required')
            url = f'{self.britive.base_url}/v1/approvals/consumer/papservice/resource?resourceId=' \
                  f'{profile_id}/{environment_id}'

        return self.britive.delete(url)

    def checkout(self, profile_id: str, environment_id: str, programmatic: bool = True,
                 include_credentials: bool = False, justification: str = None, wait_time: int = 60,
                 max_wait_time: int = 600, progress_func: Callable = None) -> dict:
        """
        Checkout a profile.

        If the profile has already been checked out this method will return the details of the checked out profile.

        If approval is required, this method will continue to check if approval has been obtained. Once the request
        is approved the profile will be checked out. Sending a `SIGINT/KeyboardInterrupt/Ctrl+C/^C` while waiting for
        the approval request to be dispositioned will withdraw the request. Sending a second `^C` immediately after
        the first will immediately exit the program.

        Programmatic access is only available for the following cloud providers.

        - AWS
        - Azure
        - GCP

        :param profile_id: The ID of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param environment_id: The ID of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param programmatic: True for programmatic credential checkout. False for console checkout.
        :param include_credentials: True if tokens should be included in the response. False if the caller wishes to
            call `credentials()` at a later time. If True, the `credentials` key will be included in the response which
            contains the response from `credentials()`. Setting this parameter to `True` will result in a synchronous
            call vs. setting to `False` will allow for an async call.
        :param justification: Optional justification if checking out the profile requires approval.
        :param wait_time: The number of seconds to sleep/wait between polling to check if the profile checkout
            was approved.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
        :return: Details about the checked out profile, and optionally the credentials generated by the checkout.
        :raises ApprovalRequiredButNoJustificationProvided: if approval is required but no justification is provided.
        :raises ApprovalWorkflowTimedOut: if max_wait_time has been reached while waiting for approval.
        :raises ApprovalWorkflowRejected: if the request to check out the profile was rejected.
        :raises ProfileApprovalTimedOut: if the approval request timed out (exceeded the max time as specified by the
            profile policy.
        :raises ProfileApprovalRejected: if the approval request was rejected by the approver.
        :raises ProfileApprovalWithdrawn: if the approval request was withdrawn by the requester.
        """

        params = {
            'accessType': 'PROGRAMMATIC' if programmatic else 'CONSOLE'
        }

        data = {
            'justification': justification
        }

        transaction = None

        # let's see if there is already a checked out profile
        progress_pending_checked_out_profiles_sent = False
        while True:  # will break the loop when needed
            loop = False
            if progress_func and not progress_pending_checked_out_profiles_sent:
                progress_func('reviewing currently checked out profiles')
                progress_pending_checked_out_profiles_sent = True
            for p in self.list_checked_out_profiles():
                right_profile = p['papId'] == profile_id
                right_env = p['environmentId'] == environment_id
                right_type = p['accessType'] == params['accessType']
                if all([right_profile, right_env, right_type]):
                    if p['checkedIn'] is None:  # still currently checked out so we can move on
                        transaction = p
                        break
                    else:  # we are in the middle of a profile being checked in so cannot check it out yet
                        loop = True
            if loop:
                if progress_func:
                    progress_func('pending profile checkin')
                time.sleep(1)
            else:
                break

        # if not check it out
        if not transaction:
            try:
                transaction = self.britive.post(
                    f'{self.base_url}/{profile_id}/environments/{environment_id}',
                    params=params,
                    json=data
                )
            except exceptions.InvalidRequest as e:
                if 'MA-0009' in str(e):  # old approval process that coupled approval and checkout
                    raise exceptions.ApprovalRequiredButNoJustificationProvided()
                if 'MA-0010' in str(e):  # new approval process that de-couples approval from checkout
                    # if the caller has not provided a justification we know for sure the call will fail
                    # so raise the exception
                    if not justification:
                        raise exceptions.ApprovalRequiredButNoJustificationProvided()

                    # request approval
                    status = self.request_approval(
                        profile_id=profile_id,
                        environment_id=environment_id,
                        justification=justification,
                        wait_time=wait_time,
                        max_wait_time=max_wait_time,
                        block_until_disposition=True,
                        progress_func=progress_func
                    )

                    # handle the response based on the value of status
                    if status == 'approved':
                        transaction = self.britive.post(
                            f'{self.base_url}/{profile_id}/environments/{environment_id}',
                            params=params,
                            json=data
                        )
                    else:
                        raise approval_exceptions[status]
                else:
                    raise e

        transaction_id = transaction['transactionId']

        # this approval workflow logic is for the legacy workflow when approval and checkout were coupled together
        # this logic can be removed once the new approval logic is deployed to production.
        if transaction['status'] == 'checkOutInApproval':  # wait for approval or until timeout occurs
            quit_time = time.time() + max_wait_time
            while True:
                try:
                    transaction = self.get_checked_out_profile(transaction_id=transaction_id)
                except exceptions.TransactionNotFound:
                    raise exceptions.ApprovalWorkflowRejected()
                if transaction['status'] == 'checkOutInApproval':  # we have an approval workflow occurring
                    if time.time() >= quit_time:
                        raise exceptions.ApprovalWorkflowTimedOut()
                    if progress_func:
                        progress_func('awaiting approval')
                    time.sleep(wait_time)
                    continue
                else:  # status == checkedOut
                    break

        # inject credentials if asked
        if include_credentials:
            # if the transaction is not in status of checkedOut here it will be after the
            # return of this call and we update the transaction object accordingly
            credentials, transaction = self.credentials(
                transaction_id=transaction_id,
                transaction=transaction,
                return_transaction_details=True,
                progress_func=progress_func
            )
            transaction['credentials'] = credentials

        if progress_func:
            progress_func('complete')
        return transaction

    def checkout_by_name(self, profile_name: str, environment_name: str, application_name: str = None,
                         programmatic: bool = True, include_credentials: bool = False, justification: str = None,
                         wait_time: int = 60, max_wait_time: int = 600, progress_func: Callable = None) -> dict:
        """
        Checkout a profile by supplying the names of entities vs. the IDs of those entities.

        If approval is required, this method will continue to check if approval has been obtained. Once the request
        is approved the profile will be checked out. Sending a `SIGINT/KeyboardInterrupt/Ctrl+C/^C` while waiting for
        the approval request to be dispositioned will withdraw the request. Sending a second `^C` immediately after
        the first will immediately exit the program.

        Programmatic access is only available for the following cloud providers.

        - AWS
        - Azure
        - GCP

        :param profile_name: The name of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param environment_name: The name of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param application_name: Optionally the name of the application, which can help disambiguate between profiles
            with the same name across applications.
        :param programmatic: True for programmatic credential checkout. False for console checkout.
        :param include_credentials: True if tokens should be included in the response. False if the caller wishes to
            call `credentials()` at a later time. If True, the `credentials` key will be included in the response which
            contains the response from `credentials()`. Setting this parameter to `True` will result in a synchronous
            call vs. setting to `False` will allow for an async call.
        :param justification: Optional justification if checking out the profile requires approval.
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

        ids = self._get_profile_and_environment_ids_given_names(profile_name, environment_name, application_name)

        return self.checkout(
            profile_id=ids['profile_id'],
            environment_id=ids['environment_id'],
            programmatic=programmatic,
            include_credentials=include_credentials,
            justification=justification,
            wait_time=wait_time,
            max_wait_time=max_wait_time,
            progress_func=progress_func
        )

    def credentials(self, transaction_id: str, transaction: dict = None, return_transaction_details: bool = False,
                    progress_func: Callable = None) -> any:
        """
        Return credentials of a checked out profile given the transaction ID.

        Will automatically determine the type of checkout (programmatic or console) and return the appropriate
        details.

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
                else:  # status == checkedOut
                    break

        # step 2: make the proper API call
        url_part = 'url' if transaction['accessType'] == 'CONSOLE' else 'tokens'
        creds = self.britive.get(f'{self.base_url}/{transaction_id}/{url_part}')

        if return_transaction_details:
            return creds, transaction
        else:
            return creds

    def checkin(self, transaction_id: str) -> dict:
        """
        Check in a checked out profile.

        :param transaction_id: The ID of the transaction.
        :return: Details of the checked in profile.
        """

        params = {
            'type': 'API'
        }
        return self.britive.put(f'{self.base_url}/{transaction_id}', params=params)

    def checkin_by_name(self, profile_name: str, environment_name: str, application_name: str = None) -> dict:
        """
        Check in a checked out profile by supplying the names of entities vs. the IDs of those entities

        :param profile_name: The name of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param environment_name: The name of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param application_name: Optionally the name of the application, which can help disambiguate between profiles
            with the same name across applications.
        :return: Details of the checked in profile.
        """

        ids = self._get_profile_and_environment_ids_given_names(profile_name, environment_name, application_name)

        transaction_id = None
        for profile in self.list_checked_out_profiles():
            if profile['environmentId'] == ids['environment_id'] and profile['papId'] == ids['profile_id']:
                transaction_id = profile['transactionId']
                break
        if not transaction_id:
            raise ValueError(f'no checked out profile found for the given profile_name and environment_name')

        return self.checkin(transaction_id=transaction_id)

    def frequents(self) -> list:
        """
        Return list of frequently used profiles for the user.

        :return: List of profiles.
        """

        return self.britive.get(f'{self.base_url}/frequently-used')

    def favorites(self) -> list:
        """
        Return list of favorite profiles for the user.

        :return: List of profiles.
        """

        return self.britive.get(f'{self.base_url}/favorites')

    def whoami(self) -> dict:
        """
        Return details about the currently authenticated identity (user or service).

        :return: Details of the currently authenticated identity.
        """

        return self.britive.post(f'{self.britive.base_url}/auth/validate')['authenticationResult']

    def _get_profile_and_environment_ids_given_names(self, profile_name: str, environment_name: str,
                                                     application_name: str = None) -> dict:
        ids = None
        profile_found = False
        environment_found = False

        # collect relevant profile/environment combinations to which the identity is entitled
        for app in self.list_profiles():
            app_name = app['appName'].lower()
            if application_name and app_name != application_name.lower():  # restrict to one app if provided
                continue
            for profile in app['profiles']:
                prof_name = profile['profileName'].lower()
                prof_id = profile['profileId']

                if prof_name == profile_name.lower():
                    profile_found = True
                    for env in profile['environments']:
                        env_name = env['environmentName'].lower()
                        env_id = env['environmentId']

                        if env_name == environment_name.lower():
                            environment_found = True
                            # lets check to see if `ids` has already been set
                            # if so we should error because we don't know which name combo to use
                            if ids:
                                raise ValueError(
                                    f'multiple combinations of profile `{profile_name}` and environment '
                                    f'`{environment_name}` exist so no unique combination can be determined. Please '
                                    f'provide the optional parameter `application_name` to clarify which application '
                                    f'the environment belongs to.'
                                )
                            # set the IDs the first time
                            ids = {
                                'profile_id': prof_id,
                                'environment_id': env_id
                            }

        # do some error checking
        if not profile_found:
            raise ValueError(f'profile `{profile_name}` not found.')

        if profile_found and not environment_found:
            raise ValueError(f'profile `{profile_name}` found but not in environment `{environment_name}`.')

        # if we get here we found both the profile and environment and they are unique so
        # we can use the `ids` dict with confidence
        return ids
