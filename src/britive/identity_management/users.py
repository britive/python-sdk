import warnings

from britive.exceptions import (
    UserNotAllowedToChangePassword,
    UserNotAssociatedWithDefaultIdentityProvider,
)

from ._identities import _Identities, _validate_identity_id


class EnableMFA:
    """`users.enable_mfa()`, kept as an object so the deprecated `users.enable_mfa.enable()` still works."""

    def __init__(self, britive) -> None:
        self.britive = britive

    def __call__(self) -> dict:
        """Start TOTP registration for the authenticated user.

        This request can return a step-up authentication challenge. Generating a secret does not complete enrollment;
        the registration flow also requires OTP validation.

        :return: Step-up authentication or TOTP registration challenge details.
        """
        return self.britive.post(f'{self.britive.base_url}/mfa/register/TOTP', json={'action': 'GENERATE_SECRET'})

    def enable(self) -> dict:
        """Deprecated alias for `users.enable_mfa()`, to be removed in the next major release."""
        warnings.warn(
            'users.enable_mfa.enable() is deprecated and will be removed in the next major release; '
            'call users.enable_mfa() instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        return self()


class Users(_Identities):
    def __init__(self, britive) -> None:
        super().__init__(britive, identity_type='User')
        self.enable_mfa = EnableMFA(britive)

    def get(self, user_id: str) -> dict:
        """
        Provide details of the given user.

        :param user_id: The ID  of the user.
        :return: Details of the specified user.
        :raises NotFound: if the identity does not exist or is not a human user.
        """

        return self._get(user_id)

    def create(self, idp: str = None, **kwargs) -> dict:
        """
        Create a new user record.

        :param idp: The ID of the IdP with which to associate the user. If not specified will default to
            the Britive identity provider.
        :param kwargs: Valid fields are...
            email - required
            username - required
            password - required only if no `idp` is provided, otherwise the IdP will handle authentication
            lastName - required
            firstName - required
            mobile
            phone
            description
            managerId
            externalId
            attributes
            relationships
            sharePasswordToUser
            emailList
            status - valid values are active, inactive - if omitted then will default to active
            adminRoles - in format [{'name': 'TenantAdmin},]
        :return: Details of the newly created user.
        """

        required_fields = ['email', 'username', 'lastName', 'firstName', 'status']

        if idp:
            kwargs['identityProvider'] = {'id': idp}
        else:
            required_fields.append('password')

        return self._create(kwargs, required_fields=required_fields)

    def update(self, user_id: str, **kwargs) -> dict:
        """
        Update the specified attributes of the provided user.

        :param user_id: The ID of the user to update
        :param kwargs: API fields to update, including `username`, `email`, `firstName`, `lastName`, `mobile`,
            `phone`, `description`, `managerId`, `identityProvider`, `externalId`, `landingPage`, and `attributes`.
            Use `enable` and `disable` to change status. The API treats `attributes` as a replacement list.
        :return: A dict containing the newly updated user details
        :raises NotFound: if `username` or `email` is omitted and the identity does not exist or is not a human user.
        :raises DoesNotExistError: if both are supplied and the identity does not exist.
        :raises UserUpdateError: if both are supplied and the identity is not a human user. Nothing is changed.
        """

        return self._update(user_id, **kwargs)

    def _prepare_update(self, identity_id: str, fields: dict) -> dict:
        if 'username' not in fields or 'email' not in fields:
            user = self._get(identity_id)
            fields.setdefault('username', user['username'])
            fields.setdefault('email', user['email'])
        return fields

    def delete(self, user_id: str) -> None:
        """
        Delete a user.

        :param user_id: The ID of the user to delete
        :return: None
        :raises NotFound: if the identity does not exist or is not a human user.
        """

        self._delete(user_id)

    def enable(self, user_id: str = None, user_ids: list = None) -> object:
        """
        Enable the given user(s).

        You can pass in both `user_id` for a single user and `user_ids` to enable multiple users in one call. If both
        `user_id` and `user_ids` are provided they will be merged together into one list.

        :param user_id: The ID of the user you wish to enable.
        :param user_ids: A list of user IDs that you wish to enable. Usernames and emails are not accepted.
        :return: if `user_ids` is set will return a list of user records, else returns a user dict
        :raises ValueError: if no IDs are provided or IDs are not non-empty strings in a list or single-ID argument.
        :raises NotFound: without an ID list, if the identity does not exist or is not a human user.
        :raises DoesNotExistError: with an ID list, if any identity does not exist or is not a human user.
        """

        return self._set_status('enabled', identity_id=user_id, identity_ids=user_ids)

    def disable(self, user_id: str = None, user_ids: list = None) -> object:
        """
        Disable the given user(s).

        You can pass in both `user_id` for a single user and `user_ids` to disable multiple users at in one call.
        If both `user_id` and `user_ids` are provided they will be merged together into one list.

        :param user_id: The ID of the user you wish to disable.
        :param user_ids: A list of user IDs that you wish to disable. Usernames and emails are not accepted.
        :return: if `user_ids` is set will return a list of user records, else returns a user dict
        :raises ValueError: if no IDs are provided or IDs are not non-empty strings in a list or single-ID argument.
        :raises NotFound: without an ID list, if the identity does not exist or is not a human user.
        :raises DoesNotExistError: with an ID list, if any identity does not exist or is not a human user.
        """

        return self._set_status('disabled', identity_id=user_id, identity_ids=user_ids)

    def reset_password(self, user_id: str, password: str) -> None:
        """
        Reset a user's password.

        Only applicable for users using the default Britive IdP.

        :param user_id: The ID of the user for which the password will be reset.
        :param password: The new password. Must match the password policy of
            at least 8 characters
            at least 1 uppercase character
            at least 1 lowercase character
            at least 1 digit
            at least 1 symbol
        :return: None
        """

        user = self.get(user_id)
        if not user['canChangeOrResetPassword']:
            raise UserNotAllowedToChangePassword

        if user['identityProvider']['type'] != 'DEFAULT':
            raise UserNotAssociatedWithDefaultIdentityProvider

        return self.britive.post(f'{self.base_url}/{user_id}/resetpassword', json={'password': password})

    def reset_mfa(self, user_id: str) -> None:
        """
        Reset a user's MFA by deleting all of the user's MFA factor registrations.

        The user will be prompted to re-establish MFA the next time it is required.

        :param user_id: The ID of the user for which MFA will be reset. Usernames and other identifiers are not
            accepted.
        :return: None
        """

        _validate_identity_id(user_id)
        self.britive.delete(f'{self.britive.base_url}/mfa/admin/registrations/users/{user_id}')

    def minimized_user_details(self, user_id: str = None, user_ids: list = None) -> list:
        """
        Retrieve a small set of user fields given a user id.

        :param user_id: The ID of the user. Will be combined with `user_ids`.
        :param user_ids: The list of user ids. Will be combined with `user_id`.
        :return: List of users with a small set of attributes.

        The API also accepts service and AI identity IDs. It does not filter by identity type and omits unknown IDs.
        """
        return self._minimized_details(user_id, user_ids)
