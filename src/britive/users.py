from .exceptions import \
    UserDoesNotHaveMFAEnabled, \
    UserNotAllowedToChangePassword, \
    UserNotAssociatedWithDefaultIdentityProvider
from .helpers.custom_attributes import CustomAttributes


valid_statues = ['active', 'inactive']


class Users:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/users'
        self.custom_attributes = CustomAttributes(self)
        self.enable_mfa = EnableMFA(britive)

    def list(self, filter_expression: str = None, include_tags: bool = False) -> list:
        """
        Provide an optionally filtered list of all users.

        :param filter_expression: filter list of users based on name, status, or role. The supported operators
             are 'eq' and 'co'. Example: 'name co "Smith"'
        :param include_tags: if this is set to true, tags/group memberships are returned.
        :return: List of user records
        """

        params = {
            'type': 'User',
            'page': 0,
            'size': 100
        }
        if filter_expression:
            params['filter'] = filter_expression
        if include_tags:
            params['includeTags'] = 'true'

        return self.britive.get(self.base_url, params)

    def get(self, user_id: str) -> dict:
        """
        Provide details of the given user.

        :param user_id: The ID  of the user.
        :return: Details of the specified user.
        """

        return self.britive.get(f'{self.base_url}/{user_id}')

    def get_by_name(self, name: str) -> list:
        """
        Return the list of users whose name contains `name`.

        :param name: The name (or part of the name) of the user you wish to get
        :return: Details of the specified users. If no user is found will return an empty list.
        """

        return self.list(filter_expression=f'name co "{name}"')

    def get_by_status(self, status: str) -> list:
        """
        Return a list of users filtered to `status`.

        :param status: valid values are `active` and `inactive`
        :return: List of users.
        """

        if status not in valid_statues:
            raise ValueError(f'status {status} not allowed.')

        return self.list(filter_expression=f'status eq "{status}"')

    def search(self, search_string: str) -> list:
        """
        Search all user fields for the given `search_string`.

        :param search_string: String to search.
        :return: List of user records.
        """

        params = {
            'type': 'User',
            'page': 0,
            'size': 100,
            'searchText': search_string
        }

        return self.britive.get(self.base_url, params)

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
            status - valid values are active, inactive - if omitted then will default to active
            adminRoles - in format [{'name': 'TenantAdmin},]
        :return: Details of the newly created user.
        """

        required_fields = [
            'email',
            'username',
            'lastName',
            'firstName',
            'status'
        ]

        kwargs['type'] = 'User'
        if idp:
            kwargs['identityProvider'] = {
                'id': idp
            }
        else:
            required_fields.append('password')

        if 'status' not in kwargs:
            kwargs['status'] = 'active'

        if kwargs['status'] not in valid_statues:
            raise ValueError(f'invalid status {kwargs["status"]}')

        if not all(x in kwargs for x in required_fields):
            raise ValueError('Not all required keyword arguments were provided.')

        response = self.britive.post(self.base_url, json=kwargs)
        return response

    def update(self, user_id: str, **kwargs) -> dict:
        """
        Update the specified attributes of the provided user.

        :param user_id: The ID of the user to update
        :param kwargs: The attributes to update for the user
        :return: A dict containing the newly updated user details
        """

        # we first have to get the existing user so we can inject the username and email into the update request
        user = self.get(user_id)

        # add some required elements to the kwargs passed in by the caller
        kwargs['type'] = 'User'

        if 'username' not in kwargs:
            kwargs['username'] = user['username']

        if 'email' not in kwargs:
            kwargs['email'] = user['email']

        self.britive.patch(f'{self.base_url}/{user_id}', json=kwargs)

        # return the updated user record
        return self.get(user_id)

    def delete(self, user_id: str) -> None:
        """
        Delete a user.

        :param user_id: The ID of the user to update
        :return: None
        """

        self.britive.delete(f'{self.base_url}/{user_id}')

    def enable(self, user_id: str = None, user_ids: list = None) -> object:
        """
        Enable the given user(s).

        You can pass in both `user_id` for a single user and `user_ids` to enable multiple users in one call. If both
        `user_id` and `user_ids` are provided they will be merged together into one list.

        :param user_id: The ID of the user you wish to enable.
        :param user_ids: A list of user IDs that you wish to enable.
        :return: if `user_ids` is set will return a list of user records, else returns a user dict
        """

        computed_users = []
        if user_ids:
            computed_users += user_ids
        if user_id:
            computed_users.append(user_id)

        # de-dup
        computed_users = list(set(computed_users))
        response = self.britive.post(f'{self.base_url}/enabled-statuses', json=computed_users)
        if not user_ids:
            return response[0]
        return response

    def disable(self, user_id: str = None, user_ids: list = None) -> object:
        """
        Disable the given user(s).

        You can pass in both `user_id` for a single user and `user_ids` to disable multiple users at in one call.
        If both `user_id` and `user_ids` are provided they will be merged together into one list.

        :param user_id: The ID of the user you wish to disable.
        :param user_ids: A list of user IDs that you wish to disable.
        :return: if `user_ids` is set will return a list of user records, else returns a user dict
        """

        computed_users = []
        if user_ids:
            computed_users += user_ids
        if user_id:
            computed_users.append(user_id)

        # de-dup
        computed_users = list(set(computed_users))
        response = self.britive.post(f'{self.base_url}/disabled-statuses', json=computed_users)
        if not user_ids:
            return response[0]
        return response

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
            raise UserNotAllowedToChangePassword()

        if user['identityProvider']['type'] != 'DEFAULT':
            raise UserNotAssociatedWithDefaultIdentityProvider()

        return self.britive.post(f'{self.base_url}/{user_id}/resetpassword', json={'password': password})

    def reset_mfa(self, user_id: str) -> None:
        """
        Reset a user's MFA.

        The user will be prompted to re-establish MFA at next login.

        :param user_id: The ID of the user for which MFA will be reset.
        :return: None
        """

        user = self.get(user_id)
        if not user['identityProvider']['mfaEnabled']:
            raise UserDoesNotHaveMFAEnabled()

        return self.britive.patch(f'{self.base_url}/{user_id}/resetmfa')

    def minimized_user_details(self, user_id: str = None, user_ids: list = None) -> list:
        """
        Retrieve a small set of user fields given a user id.

        :param user_id: The ID of the user. Will be combined with `user_ids`.
        :param user_ids: The list of user ids. Will be combined with `user_id`.
        :return: List of users with a small set of attributes.
        """
        if user_ids is None:
            user_ids = []
        if user_id and user_id not in user_ids:
            user_ids.append(user_id)
        if len(user_ids) == 0:
            return []

        return self.britive.post(f'{self.base_url}/minimized-user-details', json=user_ids)


class EnableMFA:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/mfa/register/TOTP'

    def enable(self) -> dict:
        """
        Enable MFA for user

        :return: Challenge details
        """

        data = {'action': 'GENERATE_SECRET'}
        return self.britive.post(self.base_url, json=data)
