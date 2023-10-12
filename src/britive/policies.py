from .system.policies import SystemPolicies
from typing import Union


class Policies:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/policy-admin/policies'

    @staticmethod
    def build(name: str, description: str = '', draft: bool = False, active: bool = True,
              read_only: bool = False, users: list = None, tags: list = None, tokens: list = None,
              service_identities: list = None, permissions: list = None, roles: list = None, ips: list = None,
              from_time: str = None, to_time: str = None, date_schedule: dict = None, days_schedule: dict = None,
              approval_notification_medium: Union[str, list] = None, time_to_approve: int = 5,
              access_validity_time: int = 120, approver_users: list = None, approver_tags: list = None,
              access_type: str = 'Allow', identifier_type: str = 'name', condition_as_dict: bool = False) -> dict:
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
        :param condition_as_dict: Prior to version 2.22.0 the only acceptable format for the condition block of
            a policy was as a stringifed json object. As of 2.22.0 the condition block can also be built as a raw
            python dictionary. This parameter will default to `False` to support backwards compatibility. Setting to
            `True` will result in the policy condition being returned/built as a python dictionary.
        :return: A dict which can be provided as a policy to `create` and `update`.
        """

        return SystemPolicies.build(
            name=name,
            description=description,
            draft=draft,
            active=active,
            read_only=read_only,
            users=users,
            tags=tags,
            tokens=tokens,
            service_identities=service_identities,
            permissions=permissions,
            roles=roles,
            ips=ips,
            from_time=from_time,
            to_time=to_time,
            date_schedule=date_schedule,
            days_schedule=days_schedule,
            approval_notification_medium=approval_notification_medium,
            time_to_approve=time_to_approve,
            access_validity_time=access_validity_time,
            approver_users=approver_users,
            approver_tags=approver_tags,
            access_type=access_type,
            identifier_type=identifier_type,
            condition_as_dict=condition_as_dict
        )


