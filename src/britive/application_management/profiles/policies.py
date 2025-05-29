import json
from typing import Union


class Policies:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/paps'

    def build(  # noqa: PLR0913
        self,
        name: str,
        description: str = '',
        draft: bool = False,
        active: bool = True,
        read_only: bool = False,
        users: list = None,
        tags: list = None,
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
        stepup_auth: bool = False,
        always_prompt_stepup_auth: bool = False,
        advanced_settings: dict = None,
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
        :param stepup_auth: Indicates if step-up authentication is required to checkout profile
        :param always_prompt_stepup_auth: Indicates if previous successful verification should be remembered
        :param advanced_settings: Optional Advanced Settings settings for this policy.
        :return: A dict which can be provided as a profile policy to `create` and `update`.
        """

        policy = self.britive.system.policies.build(
            name=name,
            description=description,
            draft=draft,
            active=active,
            read_only=read_only,
            users=users,
            tags=tags,
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
            stepup_auth=stepup_auth,
            always_prompt_stepup_auth=always_prompt_stepup_auth,
            advanced_settings=advanced_settings,
        )

        # clean up the generic policy response and customize for profiles
        policy.pop('permissions', None)
        policy.pop('roles', None)
        policy['consumer'] = 'papservice'

        return policy

    def list(self, profile_id: str) -> list:
        """
        List all policies associated with the provided profile.

        :param profile_id: The ID of the profile.
        :return: List of policies.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}/policies')

    def get(self, profile_id: str, policy_id: str, condition_as_dict: bool = False) -> dict:
        """
        Retrieve details about a specific policy which is associated with the provided profile.

        :param profile_id: The ID of the profile.
        :param policy_id: The ID of the policy.
        :param condition_as_dict: Prior to version 2.22.0 a policy condition block was always returned as stringified
            json. As of 2.22.0 the SDK now supports returning the condition block of a policy as either stringified json
            or a raw python dictionary. The Britive backend will also return the condition block in either format,
            depending on a query parameter value. Setting this value to `True` will result in the condition block being
            returned as a python dictionary. The default of `False` is to support backwards compatibility.
        :return: Details of the policy.
        """

        params = {'conditionJson': condition_as_dict}

        policy = self.britive.get(f'{self.base_url}/{profile_id}/policies/{policy_id}', params=params)

        # it seems profile policy is not honoring conditionJson parameter so doing some extra work here
        # to get things into the correct format. if in the future that changes we can perhaps remove
        # the below logic.
        if 'condition' in policy and condition_as_dict and isinstance(policy['condition'], str):
            policy['condition'] = json.loads(policy['condition'])

        return policy

    def create(self, profile_id: str, policy: dict) -> dict:
        """
        Create a policy associated with the provided profile.

        :param profile_id: The ID of the profile.
        :param policy: The policy contents to create.
        :return: Details of the newly created policy.
        """

        return self.britive.post(f'{self.base_url}/{profile_id}/policies', json=policy)

    def update(self, profile_id: str, policy_id: str, policy: dict) -> dict:
        """
        Update the contents of the provided policy associated with the provided profile.

        :param profile_id: The ID of the profile.
        :param policy_id: The ID of the policy.
        :param policy: The policy to update.
        :return: Details of the updated policy.
        """

        return self.britive.patch(f'{self.base_url}/{profile_id}/policies/{policy_id}', json=policy)

    def delete(self, profile_id: str, policy_id: str) -> None:
        """
        Delete the provided policy associated with the provided profile.

        :param profile_id: The ID of the profile.
        :param policy_id: The ID of the policy.
        :return: None.
        """

        return self.britive.delete(f'{self.base_url}/{profile_id}/policies/{policy_id}')
