import json
from typing import Union


class SystemPolicies:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/policy-admin/policies'

    @staticmethod
    def _validate_identifier_type(identifier_type):
        if identifier_type not in ['id', 'name']:
            raise ValueError(f'identifier_type of {identifier_type} is invalid. Only `name` and `id` are allowed.')

    def list(self) -> list:
        """
        List system level policies (not including policies for secrets manager or profiles).

        :returns: List of policies.
        """

        return self.britive.get(self.base_url)

    @staticmethod
    def format_condition_block(condition, condition_format: str):
        """
        Formats a condition block.

        Internal method used to format a policy condition block based on how the condition block was returned from the
        backend and how the caller wishes to receive the condition block.

        This method is "public" as it will be called by other methods in this SDK.
        """
        if condition_format not in ['passthrough', 'json_string', 'dict']:
            raise  ValueError(f'condition_format of {condition_format} is not valid')
        if condition_format == 'passthrough':
            return condition
        if condition_format == 'dict' and isinstance(condition, str):
            return json.loads(condition)
        if condition_format == 'json_string' and isinstance(condition, dict):
            return json.dumps(condition, default=str)
        return condition

    def get(self, policy_identifier: str, identifier_type: str = 'name', verbose: bool = False,
            condition_format: str = 'json_string') -> dict:
        """
        Get details of the specified system policy.

        :param policy_identifier: The ID or name of the policy.
        :param identifier_type: Valid values are `id` or `name`. Defaults to `name`. Represents which type of
            identifiers will be returned. Either all identifiers must be names or all identifiers must be IDs.
        :param verbose: Whether to return a more compact response (the default) or a more verbose response.
        :param condition_format: Prior to version 2.22.0 a policy condition block was always returned as stringified
            json. As of 2.22.0 the SDK now supports returning the condition block of a policy as either stringified json
            or a raw python dictionary. The Britive backend will also return the condition block in either format,
            depending on how the policy was initially created. The valid values for this parameter follow.
            * `json_string`: this is the default value in order to support backwards compatibility - will always return
                the condition block as stringified json regardless of how the policy was created
            * `dict`: will return the condition block as a python dictionary regardless of how the policy was created
            * `passthrough`: will return the condition block in whatever format it was created with - no modifications
                will be performed to the data returned from the backend
        :returns: Details of the specified policy.
        """

        self._validate_identifier_type(identifier_type)
        params = {
            'compactResponse': not verbose
        }

        policy = self.britive.get(f'{self.base_url}/{policy_identifier}', params=params)

        if 'condition' in policy.keys():
            policy['condition'] = self.format_condition_block(policy['condition'], condition_format)
        return policy

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
        return {
            'action': action,
            'resource': resource,
            'consumer': consumer
        }

    @staticmethod
    def _time_of_access_type_from_deprecated_fields(from_time: str, to_time: str):
        if len(from_time) == 8 and len(to_time) == 8:
            return 'days'
        if len(from_time) == 19 and len(to_time) == 19:
            return 'date'
        raise ValueError('from_time and to_time must both be valid times or datetimes. Cannot mix.')

    @staticmethod
    def build(name: str, description: str = '', draft: bool = False, active: bool = True,
              read_only: bool = False, users: list = None, tags: list = None, tokens: list = None,
              service_identities: list = None, permissions: list = None, roles: list = None, ips: list = None,
              from_time: str = None, to_time: str = None, date_schedule: dict = None, days_schedule: dict = None,
              approval_notification_medium: Union[str, list] = None, time_to_approve: int = 5,
              access_validity_time: int = 120, approver_users: list = None, approver_tags: list = None,
              access_type: str = 'Allow', identifier_type: str = 'name', condition_format: str = 'json_string') -> dict:
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
        :param from_time: The start date/time of when the policy is in effect. If a date is provided
            (`YYYY-MM-DD HH:MM:SS`) this will represent the start date/time of 1 contiguous time range. If just a
            time is provided (`HH:MM:SS`) this will represent the daily recurring start time. If this parameter is
            provided then `to_time` must also be provided. This parameter is deprecated as of v2.19.0. The presence of
            `date_schedule` and/or `days_schedule` will override this field.
        :param to_time: The end date/time of when the policy is in effect. If a date is provided
            (`YYYY-MM-DD HH:MM:SS`) this will represent the end date/time of 1 contiguous time range. If just a
            time is provided (`HH:MM:SS`) this will represent the daily recurring end time. If this parameter is
            provided then `from_time` must also be provided. This parameter is deprecated as of v2.19.0. The presence of
            `date_schedule` and/or `days_schedule` will override this field.
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
        :param condition_format: Prior to version 2.22.0 the only acceptable format for the condition block of
            a policy was as a stringifed json object. As of 2.22.0 the condition block can also be built as a raw
            python dictionary. This parameter will default to `json_string` to support backwards compatibility. The
            other acceptable value is `dict`. As of 2.22.0 the Britive backend supports providing the condition block
            in either format.
        :return: A dict which can be provided as a policy to `create` and `update`.
        """

        if condition_format not in ['json_string', 'dict']:
            raise ValueError(f'condition format of {condition_format} is not acceptable - only `json_string` '
                             f'and `dict` are allowed values')

        condition = {}

        # handle ip address logic
        if ips:
            condition['ipAddress'] = ','.join(ips)

        # handle from_time and to_time logic
        # this logic is deprecated (and updated) in v2.19.0 and will be retired in v3.x.x
        if from_time and not to_time:
            raise ValueError('if from_time is provided then to_time must also be provided.')
        if to_time and not from_time:
            raise ValueError('if to_time is provided then from_time must also be provided.')
        if from_time and to_time:
            # we need to determine if we are dealing with dates or times
            # as that will inform if we set days_schedule or date_schedule
            time_of_access_type = SystemPolicies._time_of_access_type_from_deprecated_fields(from_time, to_time)
            if time_of_access_type == 'days' and not days_schedule:  # dealing with times of day
                days_schedule = {
                    'fromTime': from_time,
                    'toTime': to_time,
                    'timezone': 'UTC',
                    'days': [
                        'MONDAY',
                        'TUESDAY',
                        'WEDNESDAY',
                        'THURSDAY',
                        'FRIDAY',
                        'SATURDAY',
                        'SUNDAY'
                    ]
                }
            if time_of_access_type == 'date' and not date_schedule:  # dealing with date range
                date_schedule = {
                    'fromDate': from_time,
                    'toDate': to_time,
                    'timezone': 'UTC'
                }

        if date_schedule or days_schedule:
            condition['timeOfAccess'] = {
                'dateSchedule': date_schedule,
                'daysSchedule': days_schedule
            }

        # handle approval logic
        if approval_notification_medium:
            if not approver_users and not approver_tags:
                raise ValueError('when approval is required either approver_tags or approver_users or both '
                                 'must be provided')
            approval_condition = {
                'notificationMedium': approval_notification_medium,
                'timeToApprove': time_to_approve,
                'validFor': access_validity_time,
                'isValidForInDays': False,  # the SDK will only support minutes
                'approvers': {
                    'userIds': approver_users,
                    'tags': approver_tags
                }
            }

            if not approver_users:
                approval_condition['approvers'].pop('userIds')
            if not approver_tags:
                approval_condition['approvers'].pop('tags')

            condition['approval'] = approval_condition

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
                'tokens': [{identifier_type: t} for t in tokens] if tokens else None
            }
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
        if condition:
            policy['condition'] = json.dumps(condition, default=str) if condition_format == 'json_string' else condition

        return policy
