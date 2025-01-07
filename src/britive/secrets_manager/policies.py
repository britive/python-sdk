from typing import Union


class PasswordPolicies:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager/pwdpolicies'

    def get(self, password_policy_id: str) -> dict:
        """
        Provide details of the given password policy, from a password policy id.

        :param password_policy_id: The ID  of the password policy.
        :return: Details of the specified password policy.
        """

        return self.britive.get(f'{self.base_url}/{password_policy_id}')

    def list(self, filter_str: str = None) -> list:
        """
        Provide a list of all password policies

        :param filter_str: filter to apply to the listing
        :return: List of all password policies
        """

        params = {}
        if filter_str:
            params['filter'] = filter_str

        return self.britive.get(self.base_url, params=params)

    def create(
        self,
        name: str,
        description: str = 'Default description',
        password_type: str = 'alphanumeric',
        min_password_length: int = 8,
        has_upper_case_chars: bool = True,
        has_lower_case_chars: bool = True,
        has_numbers: bool = True,
        has_special_chars: bool = True,
        allowed_special_chars: str = '~`!@#$%^&*()-_+=[]{}|/;:"?/\\.><,\'',
    ) -> dict:
        """
        Creates a new password policy.

        :param name: required, name of the password policy
        :param description: description of the password policy
        :param password_type: type of password to use for the policy
        :param min_password_length: minimum length of the password
        :param has_upper_case_chars: whether to require uppercase characters
        :param has_lower_case_chars: whether to require lowercase characters
        :param has_numbers: whether to require numbers
        :param has_special_chars: whether to require special characters
        :param allowed_special_chars: a string of special characters to allow in the password
        :return: Details of the newly created password policy.
        """

        params = {
            'name': name,
            'description': description,
            'passwordType': password_type,
            'minPasswordLength': min_password_length,
            'hasUpperCaseChars': has_upper_case_chars,
            'hasLowerCaseChars': has_lower_case_chars,
            'hasNumbers': has_numbers,
            'hasSpecialChars': has_special_chars,
            'allowedSpecialChars': allowed_special_chars,
        }
        return self.britive.post(self.base_url, json=params)

    def create_pin(self, name: str, description: str = 'Default description', pin_length: int = 4) -> dict:
        """
        Creates a new pin password policy.

        :param name: required, name of the pin password policy
        :param description: description of the pin password policy
        :param pin_length: length of the pin to use for the policy
        :return: Details of the newly created pin password policy.
        """

        params = {
            'name': name,
            'description': description,
            'pinLength': pin_length,
            'passwordType': 'pin',
        }
        return self.britive.post(self.base_url, json=params)

    def update(self, password_policy_id: str, **kwargs) -> None:
        """
        Updates a password policy.

        :param password_policy_id: the ID of the password policy
        :param kwargs: Valid fields are...
            name: name of the password policy
            description: description of the password policy
            passwordType: type of password to use for the policy
            minPasswordLength: minimum length of the password
            hasUpperCaseChars: whether to require uppercase characters
            hasLowercaseChars: whether to require lowercase characters
            hasNumbers: whether to require numbers
            hasSpecialChars: whether to require special characters
            allowedSpecialChars: a string of special characters to allow in the password
            pinLength: the length of the pin to use for the policy (only for pins)
        :return: None
        """

        current = self.get(password_policy_id=password_policy_id)

        return self.britive.patch(f'{self.base_url}/{password_policy_id}', json={**current, **kwargs})

    def delete(self, password_policy_id: str) -> None:
        """
        Deletes a password policy.

        :param password_policy_id: the ID of the password policy
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{password_policy_id}')

    def generate_password(self, password_policy_id: str) -> dict:
        """
        Generates a password for the given password policy.

        :param password_policy_id: the ID of the password policy
        :return: the generated password
        """

        params = {'action': 'generatePasswordOrPin'}
        return self.britive.get(f'{self.base_url}/{password_policy_id}', params=params)['passwordOrPin']

    def validate(self, password_policy_id: str, password: str) -> dict:
        """
        Validates a password for the given password policy.

        :param password_policy_id: the ID of the password policy
        :param password: the password to validate
        :return: whether the password is valid
        """

        data = {
            'id': password_policy_id,
            'passwordOrPin': password,
        }

        params = {'action': 'validatePasswordOrPin'}
        return self.britive.post(self.base_url, json=data, params=params)


class Policies:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/policy-admin/policies'

    def list(self, path: str = '/', filter_str: str = None) -> dict:
        """
        Gets all policies in the vault.

        :param path: path of the policy, include the / at the beginning
        :param filter_str: filter to apply to the listing
        :return: Details of the policies.
        """

        params = {'resource': path, 'consumer': 'secretmanager'}
        if filter_str:
            params['filter'] = filter_str
        return self.britive.get(f'{self.base_url}', params=params)

    def delete(self, policy_id: str, path: str = '/') -> None:
        """
        Deletes a policy from the vault.

        :param policy_id: ID of the policy to delete
        :param path: path of the policy, include the / at the beginning
        :return: None
        """

        params = {'consumer': 'secretmanager', 'resource': path}
        return self.britive.delete(f'{self.base_url}/{policy_id}', params=params)

    def build(  # noqa: PLR0913
        self,
        name: str,
        access_level: str = None,
        description: str = '',
        draft: bool = False,
        active: bool = True,
        read_only: bool = False,
        users: list = None,
        tags: list = None,
        tokens: list = None,
        service_identities: list = None,
        ips: list = None,
        date_schedule: dict = None,
        days_schedule: dict = None,
        approval_notification_medium: Union[str, list] = None,
        time_to_approve: int = 5,
        access_validity_time: int = 120,
        approver_users: list = None,
        approver_tags: list = None,
        access_type: str = 'Allow',
        identifier_type: str = 'name',
        condition_as_dict: bool = False,
    ) -> dict:
        """
        Build a policy document given the provided inputs.

        :param name: The name of the policy.
        :param access_level: The level of access. Valid values are SM_View, SM_Manage, SM_CRUD. Defaults to SM_View
            if not provided.
        :param description: An optional description of the policy.
        :param draft: Indicates if the policy is a draft. Defaults to `False`.
        :param active: Indicates if the policy is active. Defaults to `True`.
        :param read_only: Indicates if the policy is a read only. Defaults to `False`.
        :param users: Optional list of user names or ids to which this policy applies.
        :param tags: Optional list of tag names or ids to which this policy applies.
        :param tokens: Optional list of token names or ids to which this policy applies.
        :param service_identities: Optional list of service identity names or ids to which this policy applies.
        :param ips: Optional list of IP addresses for which this policy applies. Provide in CIDR notation
            or dotted decimal format for individual (/32) IP addresses.
        :param date_schedule: A dict in the format
            {
                'fromDate': '2022-10-29 10:30:00',
                'toDate': '2022-11-05 18:30:00',
                'timezone': 'UTC'
            }
            Timezone formats can be found in the TZ Identifier column of the following page.
            https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        :param days_schedule: A dict in the format
            {
                'fromTime': '10:30:00',
                'toTime': '18:30:00',
                'timezone': 'UTC',
                'days': ['MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY']
            }
            Timezone formats can be found in the TZ Identifier column of the following page.
            https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        :param approval_notification_medium: Optional notification medium name to which approval requests will be
            delivered. Can also specify a list of notification medium names. Specifying this parameter indicates the
            desire to enable approvals for this policy.
        :param time_to_approve: Optional number of minutes to wait for an approval before denying the action. Defaults
            to 5 minutes.
        :param access_validity_time: Optional number of minutes the access is valid after approval. Defaults to 120
            minutes.
        :param approver_users: Optional list of user names or ids who are to be considered approvers.
            If `approval_notification_medium` is set then either `approver_users` or `approver_tags` is required.
        :param approver_tags: Optional list of tag names who are considered approvers.
            If `approval_notification_medium` is set then either `approver_users` or `approver_tags` is required.
        :param access_type: The type of access this policy provides. Valid values are `Allow` and `Deny`. Defaults
            to `Allow`.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers are being provided to the other parameters. Either all identifiers must be names or all
            identifiers must be IDs.
        :param condition_as_dict: Prior to version 2.22.0 the only acceptable format for the condition block of
            a policy was as a stringifed json object. As of 2.22.0 the condition block can also be built as a raw
            python dictionary. This parameter will default to `False` to support backwards compatibility. Setting to
            `True` will result in the policy condition being returned/built as a python dictionary.
        :return: A dict which can be provided as a secret manager policy to `create` and `update`.
        """

        policy = self.britive.system.policies.build(
            name=name,
            description=description,
            draft=draft,
            active=active,
            read_only=read_only,
            users=users,
            tags=tags,
            tokens=tokens,
            service_identities=service_identities,
            ips=ips,
            date_schedule=date_schedule,
            days_schedule=days_schedule,
            approval_notification_medium=approval_notification_medium,
            time_to_approve=time_to_approve,
            access_validity_time=access_validity_time,
            approver_users=approver_users,
            approver_tags=approver_tags,
            access_type=access_type,
            identifier_type=identifier_type,
            condition_as_dict=condition_as_dict,
        )

        policy.pop('permissions', None)
        policy.pop('roles', None)
        policy['accessLevel'] = access_level or 'SM_View'
        policy['consumer'] = 'secretmanager'
        return policy

    def create(self, policy: dict, path: str) -> dict:
        """
        Creates  a policy in the vault.

        :param policy: policy to create
        :param path: path of the policy, include the / at the beginning
        :return: Details of the policy.
        """

        policy['resource'] = path

        return self.britive.post(f'{self.base_url}?resource={path}&consumer=secretmanager', json=policy)
