from . import exceptions
import datetime
import json


class Policies:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/policy-admin'

    @staticmethod
    def build(name: str, description: str = '', draft: bool = False, active: bool = True,
              read_only: bool = False, users: list = None, tags: list = None, tokens: list = None,
              service_identities: list = None, permissions: list = None, roles: list = None, ips: list = None,
              from_time: str = None, to_time: str = None, approval_notification_medium: str = None,
              time_to_approve: int = 5, access_validity_time: int = 120, approver_users: list = None,
              approver_tags: list = None, access_type: str = 'Allow') -> dict:
        """
        Build a policy document given the provided inputs.

        :param name: The name of the policy.
        :param description: An optional description of the policy.
        :param draft: Indicates if the policy is a draft. Defaults to `False`.
        :param active: Indicates if the policy is a active. Defaults to `True`.
        :param read_only: Indicates if the policy is a read only. Defaults to `False`.
        :param users: Optional list of user names to which this policy applies.
        :param tags: Optional list of tag names to which this policy applies.
        :param tokens: Optional list of token IDs to which this policy applies.
        :param service_identities: Optional list of service identity names to which this policy applies.
        :param permissions: Optional list of permission names this policy grants. Provide either this parameter
            or `roles`.
        :param roles: Optional list of role names to which this policy applies. Provider either this parameter
            or `permissions`.
        :param ips: Optional list of IP addresses for which this policy applies. Provide in CIDR notation
            or dotted decimal format for individual (/32) IP addresses.
        :param from_time: The start date/time of when the policy is in effect. If a date is provided
            (`YYYY-MM-DD HH:MM:SS`) this will represent the start date/time of 1 contiguous time range. If just a
            time is provided (`HH:MM:SS`) this will represent the daily recurring start time. If this parameter is
            provided then `to_time` must also be provided.
        :param to_time: The end date/time of when the policy is in effect. If a date is provided
            (`YYYY-MM-DD HH:MM:SS`) this will represent the end date/time of 1 contiguous time range. If just a
            time is provided (`HH:MM:SS`) this will represent the daily recurring end time. If this parameter is
            provided then `from_time` must also be provided.
        :param approval_notification_medium: Optional notification medium name to which approval requests will be
            delivered. Specifying this parameter indicates the desire to enable approvals for this policy.
        :param time_to_approve: Optional number of minutes to wait for an approval before denying the action. Defaults
            to 5 minutes.
        :param access_validity_time: Optional number of minutes the access is valid after approval. Defaults to 120
            minutes.
        :param approver_users: Optional list of user names who are to be considered approvers.
            If `approval_notification_medium` is set then either `approver_users` or `approver_tags` is required.
        :param approver_tags: Optional list of tag names who are considered approvers.
            If `approval_notification_medium` is set then either `approver_users` or `approver_tags` is required.
        :param access_type: The type of access this policy provides. Valid values are `Allow` and `Deny`. Defaults
            to `Allow`.
        :return: A dict which can be provided as a profile policy to `create` and `update`.
        """

        condition = {}

        # handle ip address logic
        if ips:
            condition['ipAddress'] = ','.join(ips)

        # handle from_time and to_time logic
        if from_time and not to_time:
            raise ValueError('if from_time is provided then to_time must also be provided.')
        if to_time and not from_time:
            raise ValueError('if to_time is provided then from_time must also be provided.')
        if from_time and to_time:
            condition['timeOfAccess'] = {
                'from': from_time,
                'to': to_time
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
                'users': [{'name': u} for u in users] if users else None,
                'tags': [{'name': t} for t in tags] if tags else None,
                'serviceIdentities': [{'name': s} for s in service_identities] if service_identities else None,
                'tokens': [{'name': t} for t in tokens] if tokens else None
            },
            'condition': json.dumps(condition, default=str)
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
            policy['permissions'] = [{'name': p} for p in permissions]
        if roles:
            policy['roles'] = [{'name': r} for r in roles]

        return policy
