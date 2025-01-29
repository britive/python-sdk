import json
from typing import Union


class SystemPolicies:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/policy-admin/policies'

    @staticmethod
    def _validate_identifier_type(identifier_type) -> None:
        if identifier_type not in ['id', 'name']:
            raise ValueError(f'identifier_type of {identifier_type} is invalid. Only `name` and `id` are allowed.')

    def list(self, filter_expression: str = '') -> list:
        """
        List system level policies (not including policies for secrets manager or profiles).

        :param filter_expression: Filter based on `name`. Valid operators are `eq`, `sw`, and
            `co`. Example: name co policy
        :returns: List of policies.
        """

        params = {}
        if filter_expression:
            params['filter'] = filter_expression
        return self.britive.get(self.base_url, params=params)

    def get(
        self,
        policy_identifier: str,
        identifier_type: str = 'name',
        verbose: bool = False,
        condition_as_dict: bool = False,
    ) -> dict:
        """
        Get details of the specified system policy.

        :param policy_identifier: The ID or name of the policy.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :param verbose: Whether to return a more compact response (the default) or a more verbose response.
        :param condition_as_dict: Prior to version 2.22.0 a policy condition block was always returned as stringified
            json. As of 2.22.0 the SDK now supports returning the condition block of a policy as either stringified json
            or a raw python dictionary. The Britive backend will also return the condition block in either format,
            depending on a query parameter value. Setting this value to `True` will result in the condition block being
            returned as a python dictionary. The default of `False` is to support backwards compatibility.
        :return: Details of the specified policy.
        """

        self._validate_identifier_type(identifier_type)

        params = {'compactResponse': not verbose, 'conditionJson': condition_as_dict}

        return self.britive.get(f'{self.base_url}/{policy_identifier}', params=params)

    def create(self, policy: dict) -> dict:
        """
        Create a system level policy.

        :param policy: The policy to create. Use `policies.build` to assist in constructing a proper policy document.
        :returns: Details of the newly created policy.
        """

        return self.britive.post(self.base_url, json=policy)

    def update(self, policy_identifier: str, policy: dict, identifier_type: str = 'name') -> None:
        """
        Update a system level policy.

        :param policy_identifier: The ID or name of the policy to update.
        :param policy: The policy to update. Use `policies.build` to assist in constructing a proper policy document.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :returns: None.
        """

        self._validate_identifier_type(identifier_type)
        return self.britive.patch(f'{self.base_url}/{policy_identifier}', json=policy)

    def delete(self, policy_identifier: str, identifier_type: str = 'name') -> None:
        """
        Delete a system level policy.

        :param policy_identifier: The ID or name of the policy to delete.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :returns: None.
        """

        self._validate_identifier_type(identifier_type)
        return self.britive.delete(f'{self.base_url}/{policy_identifier}')

    def disable(self, policy_identifier: str, identifier_type: str = 'name') -> None:
        """
        Disable a system level policy.

        :param policy_identifier: The ID of the policy to disable.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :returns: None.
        """

        self._validate_identifier_type(identifier_type)
        return self.britive.patch(f'{self.base_url}/{policy_identifier}', json={'isActive': False})

    def enable(self, policy_identifier: str, identifier_type: str = 'name') -> None:
        """
        Enable a system level policy.

        :param policy_identifier: The ID of the policy to enable.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :returns: None.
        """

        self._validate_identifier_type(identifier_type)
        return self.britive.patch(f'{self.base_url}/{policy_identifier}', json={'isActive': True})

    def evaluate(self, statements: list) -> dict:
        """
        Evaluate the calling identities access for the given set of statements.

        :param: statements: List of statements in the following format. Use `build_evaluate_statement` to help
            construct the statement list.
            [
                {
                    'action': '<action>',
                    'resource': '<resource>',
                    'consumer': '<consumer>'
                },
            ]
        :returns: Dictionary containing each statement mapped to Allow or Deny.
        """

        return self.britive.post(f'{self.britive.base_url}/v1/policy-admin/batchevaluate', json=statements)

    @staticmethod
    def build_evaluate_statement(consumer: str, action: str, resource: str = '*') -> dict:
        """
        Builds a statement which can be evaluated with `evaluate`.

        :param consumer: The consumer for the statement.
        :param action: The action for the statement.
        :param resource: Optional resource for the statement. Defaults to `*`.
        :returns: The statement.
        """
        return {'action': action, 'resource': resource, 'consumer': consumer}

    @staticmethod
    def build(  # noqa: PLR0913
        name: str,
        description: str = '',
        draft: bool = False,
        active: bool = True,
        read_only: bool = False,
        users: list = None,
        tags: list = None,
        tokens: list = None,
        service_identities: list = None,
        permissions: list = None,
        roles: list = None,
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
        stepup_auth: bool = False,
        always_prompt_stepup_auth: bool = False,
    ) -> dict:
        """
        Build a policy document given the provided inputs.

        :param name: The name of the policy.
        :param description: An optional description of the policy.
        :param draft: Indicates if the policy is a draft. Defaults to `False`.
        :param active: Indicates if the policy is active. Defaults to `True`.
        :param read_only: Indicates if the policy is a read only. Defaults to `False`.
        :param users: Optional list of user names or ids to which this policy applies.
        :param tags: Optional list of tag names or ids to which this policy applies.
        :param tokens: Optional list of token names or ids to which this policy applies.
        :param service_identities: Optional list of service identity names or ids to which this policy applies.
        :param permissions: Optional list of permission names or ids this policy grants. Provide either this parameter
            or `roles`.
        :param roles: Optional list of role names or ids to which this policy applies. Provider either this parameter
            or `permissions`.
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
        :param stepup_auth: Indicates if step-up authentication is required to access the resource.
        :param always_prompt_stepup_auth: Indicates if previous successful verification should be remembered
        :return: A dict which can be provided as a policy to `create` and `update`.
        """

        condition = {}

        # handle ip address logic
        if ips:
            condition['ipAddress'] = ','.join(ips)

        if date_schedule or days_schedule:
            condition['timeOfAccess'] = {'dateSchedule': date_schedule, 'daysSchedule': days_schedule}

        # handle approval logic
        if approval_notification_medium:
            if not approver_users and not approver_tags:
                raise ValueError(
                    'when approval is required either approver_tags or approver_users or both must be provided'
                )
            approval_condition = {
                'notificationMedium': approval_notification_medium,
                'timeToApprove': time_to_approve,
                'validFor': access_validity_time,
                'isValidForInDays': False,  # the SDK will only support minutes
                'approvers': {'userIds': approver_users, 'tags': approver_tags},
            }

            if not approver_users:
                approval_condition['approvers'].pop('userIds')
            if not approver_tags:
                approval_condition['approvers'].pop('tags')

            condition['approval'] = approval_condition

        if stepup_auth:
            prompt = 'true' if always_prompt_stepup_auth else 'false'
            step_up_condition = {'factor': 'TOTP', 'alwaysPrompt': prompt}
            condition['stepUpCondition'] = step_up_condition

        # put it all together
        policy = {
            'name': name,
            'description': description,
            'isActive': active,
            'isDraft': draft,
            'isReadOnly': read_only,
            'accessType': access_type,
            'members': {
                'users': [{identifier_type: u} for u in users] if users else None,
                'tags': [{identifier_type: t} for t in tags] if tags else None,
                'serviceIdentities': [{identifier_type: s} for s in service_identities] if service_identities else None,
                'tokens': [{identifier_type: t} for t in tokens] if tokens else None,
            },
        }

        if not users:
            policy['members'].pop('users')
        if not tags:
            policy['members'].pop('tags')
        if not service_identities:
            policy['members'].pop('serviceIdentities')
        if not tokens:
            policy['members'].pop('tokens')

        if permissions:
            policy['permissions'] = [{identifier_type: p} for p in permissions]
        if roles:
            policy['roles'] = [{identifier_type: r} for r in roles]

        policy['condition'] = condition if condition_as_dict else json.dumps(condition, default=str)

        return policy
