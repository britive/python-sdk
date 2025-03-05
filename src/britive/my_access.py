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
from .exceptions.badrequest import (
    ApprovalJustificationRequiredError,
    ProfileApprovalRequiredError,
)
from .exceptions.generic import BritiveGenericError, StepUpAuthenticationRequiredError
from .helpers import HelperMethods
from .my_requests import MyAccessRequests

approval_exceptions = {
    'rejected': ProfileApprovalRejected(),
    'cancelled': ProfileApprovalWithdrawn(),
    'timeout': ProfileApprovalTimedOut(),
    'withdrawn': ProfileApprovalWithdrawn(),
}


class MyAccess:
    """
    This class is meant to be called by end users, it is an API layer on top of the actions that can be performed on the
    "My Access" page of the Britive UI.

    No "administrative" access is required by the methods in this class. Each method will only return resources/allow
    actions which are permitted to be performed by the user/service identity, as identified by an API token or
    interactive login bearer token.

    It is entirely possible that an administrator who makes these API calls could get nothing returned, as that
    administrator may not have access to any profiles.
    """

    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/access'
        self._get_profile_and_environment_ids_given_names = HelperMethods(
            self.britive
        ).get_profile_and_environment_ids_given_names

        # MyRequests
        __my_requests = MyAccessRequests(self.britive)
        self.request_approval = __my_requests.request_approval
        self.request_approval_by_name = __my_requests.request_approval_by_name
        self.withdraw_approval_request = __my_requests.withdraw_approval_request
        self.withdraw_approval_request_by_name = __my_requests.withdraw_approval_request_by_name

    def list(self, filter_text: str = None, search_text: str = None, size: int = None) -> dict:
        """
        List the access details for the current user.

        :param filter_text: filter details by key, using eq|co|sw operators, e.g. `filter_text='key co text'`
        :param search_text: filter details by search text.
        :param size: reduce the size of the response to the specified limit.
        :return: Dict of access details.
        """

        params = {'type': 'sdk'}
        if filter_text:
            params['filter'] = filter_text
        if search_text:
            params['search'] = search_text
        if size:
            params['size'] = size

        return self.britive.get(self.base_url, params=params)

    def list_profiles(self) -> list:
        """
        List the profiles for which the user has access.

        :return: List of profiles.
        """

        return self.britive.get(self.base_url)

    def list_checked_out_profiles(self, include_profile_details: bool = False) -> list:
        """
        Return list of details on currently checked out profiles for the user.

        :param include_profile_details: Include `details` for each checked out profile.
        :return: List of checked out profiles.
        """

        checked_out_profiles = self.britive.get(f'{self.base_url}/app-access-status')

        if include_profile_details:
            for profile in checked_out_profiles:
                profile['details'] = [
                    a
                    for a in self.list_profiles()
                    if profile['appContainerId'] == a['appContainerId']
                    and [p for p in a['profiles'] if profile['papId'] == p['profileId']]
                ]

        return checked_out_profiles

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

    def get_profile_settings(self, profile_id: str, environment_id: str) -> dict:
        """
        Retrieve settings of a profile.

        :param profile_id: The ID of the profile.
        :param environment_id: The ID of the environment.
        :return: Dict of the profile settings.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}/environments/{environment_id}/settings')

    def get_profile_settings_by_name(
        self, profile_name: str, environment_name: str, application_name: str = None
    ) -> dict:
        """
        Retrieve settings of a profile by name.

        :param profile_name: The name of the profile.
        :param environment_name: The name of the environment.
        :param application_name: Optionally, the name of the application.
        :return: Dict of the profile settings.
        """

        ids = self._get_profile_and_environment_ids_given_names(
            profile_name=profile_name, environment_name=environment_name, application_name=application_name
        )

        return self.get_profile_settings(profile_id=ids['profile_id'], environment_id=ids['environment_id'])

    def extend_checkout(self, transaction_id: str) -> dict:
        """
        Extend the expiration time of a currently checked out profile.

        :param transaction_id: The ID of the transaction.
        :return: Details of the given profile/transaction.
        """

        return self.britive.patch(f'{self.base_url}/extensions/{transaction_id}')

    def extend_checkout_by_name(
        self, profile_name: str, environment_name: str, application_name: str = None, programmatic: bool = True
    ) -> dict:
        """
        Extend the expiration time of a currently checked out profile by supplying the names of entities.

        :param profile_name: The name of the profile. Use `list_profiles()` to obtain the eligible profiles.
        :param environment_name: The name of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param application_name: Optionally the name of the application, which can help disambiguate between profiles
            with the same name across applications.
        :param programmatic: True for programmatic credential checkout. False for console checkout.
        :return: Details of the given profile/transaction.
        """

        ids = self._get_profile_and_environment_ids_given_names(profile_name, environment_name, application_name)
        profile_id = ids['profile_id']
        environment_id = ids['environment_id']
        access_type = 'PROGRAMMATIC' if programmatic else 'CONSOLE'

        transaction_id = None
        for transaction in self.list_checked_out_profiles():
            is_profile = transaction['papId'] == profile_id
            is_environment = transaction['environmentId'] == environment_id
            is_type = transaction['accessType'] == access_type
            if all([is_profile, is_environment, is_type]):
                transaction_id = transaction['transactionId']
                break
        if not transaction_id:
            raise TransactionNotFound
        return self.extend_checkout(transaction_id=transaction_id)

    def _checkout(
        self,
        profile_id: str,
        environment_id: str,
        include_credentials: bool = False,
        iteration_num: int = 1,
        justification: str = None,
        max_wait_time: int = 600,
        otp: str = None,
        programmatic: bool = True,
        progress_func: Callable = None,
        ticket_id: str = None,
        ticket_type: str = None,
        wait_time: int = 60,
    ) -> dict:
        params = {'accessType': 'PROGRAMMATIC' if programmatic else 'CONSOLE'}

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
                right_profile = p['papId'] == profile_id
                right_env = p['environmentId'] == environment_id
                right_type = p['accessType'] == params['accessType']
                if all([right_profile, right_env, right_type]):
                    if p['checkedIn'] is None:  # still currently checked out so we can move on
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
                    f'{self.base_url}/{profile_id}/environments/{environment_id}', params=params, json=data
                )
            except StepUpAuthenticationRequiredError as e:
                raise StepUpAuthRequiredButNotProvided(e) from e
            except (ApprovalJustificationRequiredError, ProfileApprovalRequiredError) as e:
                if not justification:
                    raise ApprovalRequiredButNoJustificationProvided(e) from e

                # request approval
                approval_request = {
                    'block_until_disposition': True,
                    'environment_id': environment_id,
                    'justification': justification,
                    'max_wait_time': max_wait_time,
                    'profile_id': profile_id,
                    'progress_func': progress_func,
                    'ticket_id': ticket_id,
                    'ticket_type': ticket_type,
                    'wait_time': wait_time,
                }
                status = self.request_approval(**approval_request)

                # handle the response based on the value of status
                if status == 'approved':
                    transaction = self.britive.post(
                        f'{self.base_url}/{profile_id}/environments/{environment_id}', params=params, json=data
                    )
                else:
                    raise approval_exceptions[status](e) from e
            except BritiveGenericError as e:
                if 'user has already checked out profile for this environment' in str(e).lower():
                    # this is a rare race condition...explained below
                    # if 2 or more calls from the same user to checkout a profile occur at the same time +/- 1/2 seconds
                    # both calls will get the list of checked out profiles and notice that the profile is not currently
                    # checked out (as the calls are made at the same time) and proceed to checkout the profile. One
                    # of the calls will "win" that race and the other call will get a http 400 response with the above
                    # error message. This is due to the first call checking out the profile and the second call making
                    # the api call to checkout the same profile...which has already been checked out. in this case we
                    # simply need to call this _checkout method again so it will realize the profile has already been
                    # checked out and poll for credentials. but we don't want to loop forever here in case some other
                    # issue is occurring so we will only allow 1 loop before raising the error
                    if iteration_num > 2:
                        raise e
                    return self._checkout(
                        environment_id=environment_id,
                        include_credentials=include_credentials,
                        iteration_num=iteration_num + 1,
                        justification=justification,
                        max_wait_time=max_wait_time,
                        otp=otp,
                        profile_id=profile_id,
                        programmatic=programmatic,
                        progress_func=progress_func,
                        ticket_id=ticket_id,
                        ticket_type=ticket_type,
                        wait_time=wait_time,
                    )
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
        environment_id: str,
        include_credentials: bool = False,
        justification: str = None,
        max_wait_time: int = 600,
        otp: str = None,
        programmatic: bool = True,
        progress_func: Callable = None,
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
        :param environment_id: The ID of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param include_credentials: True if tokens should be included in the response. False if the caller wishes to
            call `credentials()` at a later time. If True, the `credentials` key will be included in the response which
            contains the response from `credentials()`. Setting this parameter to `True` will result in a synchronous
            call vs. setting to `False` will allow for an async call.
        :param justification: Optional justification if checking out the profile requires approval.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception.
        :param otp: Optional time based one-time passcode use for step up authentication.
        :param programmatic: True for programmatic credential checkout. False for console checkout.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
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
            environment_id=environment_id,
            include_credentials=include_credentials,
            justification=justification,
            max_wait_time=max_wait_time,
            otp=otp,
            programmatic=programmatic,
            progress_func=progress_func,
            ticket_id=ticket_id,
            ticket_type=ticket_type,
            wait_time=wait_time,
        )

    def checkout_by_name(
        self,
        profile_name: str,
        environment_name: str,
        application_name: str = None,
        include_credentials: bool = False,
        justification: str = None,
        max_wait_time: int = 600,
        otp: str = None,
        programmatic: bool = True,
        progress_func: Callable = None,
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
        :param environment_name: The name of the environment. Use `list_profiles()` to obtain the eligible environments.
        :param application_name: Optionally the name of the application, which can help disambiguate between profiles
            with the same name across applications.
        :param include_credentials: True if tokens should be included in the response. False if the caller wishes to
            call `credentials()` at a later time. If True, the `credentials` key will be included in the response which
            contains the response from `credentials()`. Setting this parameter to `True` will result in a synchronous
            call vs. setting to `False` will allow for an async call.
        :param justification: Optional justification if checking out the profile requires approval.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception.
        :param otp: Optional time based one-time passcode use for step up authentication.
        :param programmatic: True for programmatic credential checkout. False for console checkout.
        :param progress_func: An optional callback that will be invoked as the checkout process progresses.
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

        ids = self._get_profile_and_environment_ids_given_names(profile_name, environment_name, application_name)

        return self._checkout(
            profile_id=ids['profile_id'],
            environment_id=ids['environment_id'],
            include_credentials=include_credentials,
            justification=justification,
            max_wait_time=max_wait_time,
            otp=otp,
            programmatic=programmatic,
            progress_func=progress_func,
            ticket_id=ticket_id,
            ticket_type=ticket_type,
            wait_time=wait_time,
        )

    def credentials(
        self,
        transaction_id: str,
        transaction: dict = None,
        return_transaction_details: bool = False,
        progress_func: Callable = None,
    ) -> Any:
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
                # status == checkedOut
                break

        # step 2: make the proper API call
        url_part = 'url' if transaction['accessType'] == 'CONSOLE' else 'tokens'
        creds = self.britive.get(f'{self.base_url}/{transaction_id}/{url_part}')

        if return_transaction_details:
            return creds, transaction
        return creds

    def checkin(self, transaction_id: str) -> dict:
        """
        Check in a checked out profile.

        :param transaction_id: The ID of the transaction.
        :return: Details of the checked in profile.
        """

        params = {'type': 'API'}
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
            raise ValueError('no checked out profile found for the given profile_name and environment_name')

        return self.checkin(transaction_id=transaction_id)

    def whoami(self) -> dict:
        """
        Return details about the currently authenticated identity (user or service).

        :return: Details of the currently authenticated identity.
        """

        return self.britive.post(f'{self.britive.base_url}/auth/validate')['authenticationResult']

    def frequents(self) -> list:
        """
        Return list of frequently used profiles for the current user.

        :return: List of profiles.
        """

        return self.britive.get(f'{self.base_url}/frequently-used')

    def favorites(self) -> list:
        """
        Return list of favorite profiles for the current user.

        :return: List of profiles.
        """

        return self.britive.get(f'{self.base_url}/favorites')

    def create_filter(self, filter_name: str, filter_properties: str) -> dict:
        """
        Create a filter for the current user.

        :param filter_name: Name of the filter.
        :param filter_properties: Dict of the filter properties.
            Filter properties:
                applications:
                    type: list
                    desc: Application ID(s)
                associations:
                    type: list
                    desc: Assocation(s)
                profiles:
                    type: list
                    desc: Profile ID(s)
                statuses:
                    type: list
                    desc: Status(es)
                application_types:
                    type: list
                    desc: Application Type(s)
        :return: Details of the created filter.
        """

        if application_types := filter_properties.pop('application_types', None):
            filter_properties['applicationTypes'] = application_types

        data = {'name': filter_name, 'filter': filter_properties}

        return self.britive.post(f'{self.base_url}/{self.whoami()["userId"]}/filters', json=data)

    def list_filters(self) -> list:
        """
        Return list of filters for the current user.

        :return: List of filters.
        """

        return self.britive.get(f'{self.base_url}/{self.whoami()["userId"]}/filters')

    def update_filter(self, filter_id: str, filter_name: str, filter_properties: str) -> dict:
        """
        Update a filter for the current user.

        :param filter_id: ID of the filter.
        :param filter_name: Name of the filter.
        :param filter_properties: Dict of the filter properties.
            Filter properties:
                applications:
                    type: list
                    desc: Application ID(s)
                associations:
                    type: list
                    desc: Assocation(s)
                profiles:
                    type: list
                    desc: Profile ID(s)
                statuses:
                    type: list
                    desc: Status(es)
                application_types:
                    type: list
                    desc: Application Type(s)
        :return: Details of the updated filter.
        """

        if application_types := filter_properties.pop('application_types', None):
            filter_properties['applicationTypes'] = application_types

        data = {'name': filter_name, 'filter': filter_properties}

        return self.britive.put(f'{self.base_url}/{self.whoami()["userId"]}/filters/{filter_id}', json=data)

    def delete_filter(self, filter_id: str) -> None:
        """
        Delete a filter for the current user.

        :param filter_id: ID of the filter.
        :return: None.
        """

        return self.britive.delete(f'{self.base_url}/{self.whoami()["userId"]}/filters/{filter_id}')
