from . import exceptions
import datetime
import json


creation_defaults = {
    'expirationDuration': 3600000,
    'extensionDuration': 1800000,
    'notificationPriorToExpiration': 300000,
    'extendable': False,
    'extensionLimit': '1',
    'status': 'active',
    'destinationUrl': '',
    'useDefaultAppUrl': True,
    'description': ''
}


class Profiles:
    def __init__(self, britive, version: int = 2):  # default to profiles v2 as v2 will be enabled for new tenants
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'
        self.version = version

        self.permissions = ProfilePermissions(britive)
        self.session_attributes = ProfileSessionAttributes(britive)

        if self.version == 1:
            self.identities = ProfileIdentities(britive)
            self.tags = ProfileTags(britive)
        elif self.version == 2:
            self.policies = ProfilePolicies(britive)
        else:
            raise Exception(f'invalid profile version - {self.version} - cannot continue')

    def __getattr__(self, name):
        if name in ['identities', 'tags'] and self.version == 2:
            raise exceptions.TenantNotEnabledForProfilesVersion1('Tenant not enabled for profiles v1')
        if name in ['policies'] and self.version == 1:
            raise exceptions.TenantNotEnabledForProfilesVersion2('Tenant not enabled for profiles v2')
        raise AttributeError(f"'Profiles' object has no attribute '{name}'")

    def create(self, application_id: str, name: str, **kwargs) -> dict:
        """
        Create a profile.

        :param application_id: The ID of the application under which the profile will be created.
        :param name: The name of the profile. This is the only required argument.
        :param kwargs: A key/value mapping consisting of the following fields. If any/all are omitted default values
            will be used. The keys and default values are provided below.

            - expirationDuration: 3600000
            - extensionDuration: 1800000
            - notificationPriorToExpiration: 300000
            - extendable: False
            - extensionLimit: '1'
            - status: 'active'
            - destinationUrl: ''
            - useDefaultAppUrl: True
            - description: ''
            - scope: if not provided no scopes will be applied. If provided it must follow the
                format listed below.

                [
                    {
                        'type': 'EnvironmentGroup'|'Environment',
                        'value':'ID'
                    },
                ]

        :return: Details of the newly created profile.
        """

        kwargs['appContainerId'] = application_id
        kwargs['name'] = name  # required field so it is being called out explicitly in the method parameters

        # merge defaults and provided information - keys in kwargs will overwrite the defaults in creation_defaults
        data = {**creation_defaults, **kwargs}  # note python 3.5 or greater but only 3.5 and up are supported so okay!

        return self.britive.post(f'{self.base_url}/{application_id}/paps', json=data)

    def list(self, application_id: str, filter_expression: str = None) -> list:
        """
        Return an optionally filtered list of profiles associated with the specified application.

        :param application_id: The ID of the application.
        :param filter_expression: Can filter based on `name`, `status`, `integrity check`. Valid operators are `eq` and
            `co`. Example: name co "Dev Account"
        :return: List of profiles.
        """

        params = {
            'page': 0,
            'size': 100,
            'view': 'summary'  # this is required - omitting it results in a 400 not authorized error
        }

        if filter_expression:
            params['filter'] = filter_expression

        return self.britive.get(f'{self.base_url}/{application_id}/paps', params=params)

    def get(self, application_id: str, profile_id: str) -> dict:
        """
        Return details of the provided profile.

        :param application_id: The ID of the application.
        :param profile_id: The ID of the profile.
        :return: Details of the profile.
        :raises: ProfileNotFound if the profile does not exist.
        """

        for profile in self.list(application_id=application_id):
            if profile['papId'] == profile_id:
                return profile

        raise exceptions.ProfileNotFound()

    def update(self, application_id: str, profile_id: str, **kwargs) -> dict:
        """
        Update details of the specified profile.

        :param application_id: The ID of the applictation.
        :param profile_id: The ID of the profile to update.
        :param kwargs: Refer to the `create()` method for details on parameters that can be provided. For this update
            action no default values will be injected for missing parameters.
        :return: Details of the updated profile.
        """

        kwargs['appContainerId'] = application_id
        return self.britive.patch(f'{self.base_url}/{application_id}/paps/{profile_id}', json=kwargs)

    def available_resources(self, profile_id: str, filter_expression: str = None) -> list:
        """
        AZURE ONLY. This API is applicable to Azure applications only.

        Returns the list of all resource scopes that are available and can be added to a profile.

        :param profile_id: The ID of the profile.
        :param filter_expression: Can filter based on `name`, `status`, `integrity check`. Valid operators are `eq` and
            `co`. Example: name co "Dev Account"
        :return: List of available resource scopes.
        """

        params = {
            'page': 0,
            'size': 100
        }

        if filter_expression:
            params['filter'] = filter_expression

        return self.britive.get(f'{self.britive.base_url}/paps/{profile_id}/resources', params=params)

    def get_scopes(self, profile_id: str) -> list:
        """
        Get the scopes associated with the specified profile.

        :param profile_id: The ID of the profile for which scopes will be updated.
        :return: List of scopes and associated details.
        """

        return self.britive.get(f'{self.britive.base_url}/paps/{profile_id}/scopes')

    def set_scopes(self, profile_id: str, scopes: list) -> list:
        """
        Update the scopes associated with the specified profile.

        :param profile_id: The ID of the profile for which scopes will be updated.
        :param scopes: List of scopes. Example  below.
            [
                {
                    'type': 'EnvironmentGroup'|'Environment',
                    'value':'ID'
                },
            ]
        :return: List of scopes and associated details.
        """

        return self.britive.post(f'{self.britive.base_url}/paps/{profile_id}/scopes', json=scopes)

    def add_single_environment_scope(self, profile_id: str, environment_id: str) -> None:
        """
        Add a single environment to the scopes associated with the specified profile.

        This API call is useful when there are a large number of environments (500+) as the
        `set_scopes()` call may time out.

        :param profile_id: The ID of the profile.
        :param environment_id: The ID of the environment which will be added to the profile scopes.
        :return: None
        """

        return self.britive.patch(f'{self.britive.base_url}/paps/{profile_id}/scopes/{environment_id}')

    def remove_single_environment_scope(self, profile_id: str, environment_id: str) -> None:
        """
        Remove a single environment from the scopes associated with the specified profile.

        This API call is useful when there are a large number of environments (500+) as the
        `set_scopes()` call may time out.

        :param profile_id: The ID of the profile.
        :param environment_id: The ID of the environment which will be removed from the profile scopes.
        :return: None
        """

        return self.britive.delete(f'{self.britive.base_url}/paps/{profile_id}/scopes/{environment_id}')

    def enable(self, application_id: str, profile_id: str) -> dict:
        """
        Enables a profile.

        :param application_id: The ID of the application.
        :param profile_id: The ID of the profile to enable.
        :return: Details of the enabled profile.
        """

        return self.britive.post(f'{self.base_url}/{application_id}/paps/{profile_id}/enabled-statuses')

    def disable(self, application_id: str, profile_id: str) -> dict:
        """
        Disables a profile.

        :param application_id: The ID of the application.
        :param profile_id: The ID of the profile to disable.
        :return: Details of the disabled profile.
        """

        return self.britive.post(f'{self.base_url}/{application_id}/paps/{profile_id}/disabled-statuses')

    def delete(self, application_id: str, profile_id: str) -> None:
        """
        Deletes a profile.

        :param application_id: The ID of the application.
        :param profile_id: The ID of the profile to delete.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{application_id}/paps/{profile_id}')


class ProfilePermissions:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/paps'

    def add(self, profile_id: str, permission_type: str, permission_name: str) -> dict:
        """
        Add a permission to a profile.

        Call `list_available()` to see what permissions can be added.

        Note that for AWS and OCI permissions are not assigned to profiles as the permissions are tied into the
        cloud provider directly (AssumeRole for AWS).

        :param profile_id: The ID of the profile.
        :param permission_type: The type of permission. Valid values are `role`, `group`, and `policy`.
        :param permission_name: The name of the permission.
        :return: Details of the permission added.
        """

        data = {
            'op': 'add',
            'permission': {
                'name': permission_name,
                'type': permission_type
            }
        }

        return self.britive.post(f'{self.base_url}/{profile_id}/permissions', json=data)

    def list_assigned(self, profile_id: str, filter_expression: str = None) -> list:
        """
        List the permissions assigned to the profile.

        :param profile_id: The ID of the profile.
        :param filter_expression: Can filter based on `name`, `status`, `integrity check`. Valid operators are `eq` and
            `co`. Example: name co "Dev Account"
        :return: List of permissions assigned to the profile.
        """

        params = {
            'page': 0,
            'size': 100
        }

        if filter_expression:
            params['filter'] = filter_expression

        return self.britive.get(f'{self.base_url}/{profile_id}/permissions', params=params)

    def list_available(self, profile_id: str) -> list:
        """
        List permissions available to be assigned to the profile.

        Note that for AWS and OCI permissions are not assigned to profiles as the permissions are tied into the
        cloud provider directly (AssumeRole for AWS).

        :param profile_id: The ID of the profile.
        :return: List of permissions that are available to be assigned to the profile.
        """

        params = {
            'page': 0,
            'size': 100,
            'query': 'available'
        }
        return self.britive.get(f'{self.base_url}/{profile_id}/permissions', params=params)

    def remove(self, profile_id: str, permission_type: str, permission_name: str) -> dict:
        """
        Remove a permission to a profile.

        :param profile_id: The ID of the profile.
        :param permission_type: The type of permission. Valid values are `role`, `group`, and `policy`.
        :param permission_name: The name of the permission.
        :return: Details of the permission removed.
        """

        data = {
            'op': 'remove',
            'permission': {
                'name': permission_name,
                'type': permission_type
            }
        }

        return self.britive.post(f'{self.base_url}/{profile_id}/permissions', json=data)


class ProfileIdentities:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/paps'

    def add(self, profile_id: str, user_id: str, start: datetime = None, end: datetime = None) -> dict:
        """
        Add a user to the profile.

        Only applicable to tenants using version 1 of profiles. If the tenant is on version 2 of profiles then use
        `britive.profiles.policies.*` instead.

        :param profile_id: The ID of the profile.
        :param user_id: The ID of the user.
        :param start: The optional start time of when the association should be in effect. Providing start implies that
            end will also be provided. `start` will be interpreted as if in UTC timezone so it is up to the caller to
            ensure that the datetime object represents UTC. Not timezone manipulation will occur.
        :param end: The optional end time of when the association should be in effect. Providing end implies that start
            will also be provided. `end` will be interpreted as if in UTC timezone so it is up to the caller to
            ensure that the datetime object represents UTC. Not timezone manipulation will occur.
        :return: Details of added user.
        """

        data = {}
        if start and end:
            data['start'] = start.isoformat(sep='T', timespec='seconds') + 'Z'
            data['end'] = end.isoformat(sep='T', timespec='seconds') + 'Z'

        return self.britive.post(f'{self.base_url}/{profile_id}/users/{user_id}', json=data)

    def list_assigned(self, profile_id: str, filter_expression: str = None) -> list:
        """
        List the users assigned to the profile.

        Only applicable to tenants using version 1 of profiles. If the tenant is on version 2 of profiles then use
        `britive.profiles.policies.*` instead.

        :param profile_id: The ID of the profile.
        :param filter_expression: Can filter based on `name`, `status`, `integrity check`. Valid operators are `eq` and
            `co`. Example: name co "Dev Account"
        :return: List of permissions assigned to the profile.
        """

        params = {
            'page': 0,
            'size': 100
        }

        if filter_expression:
            params['filter'] = filter_expression

        return self.britive.get(f'{self.base_url}/{profile_id}/users', params=params)

    def list_available(self, profile_id: str) -> list:
        """
        List users available to be assigned to the profile.

        Only applicable to tenants using version 1 of profiles. If the tenant is on version 2 of profiles then use
        `britive.profiles.policies.*` instead.

        :param profile_id: The ID of the profile.
        :return: List of users that are available to be assigned to the profile.
        """

        params = {
            'page': 0,
            'size': 100,
            'query': 'available'
        }
        return self.britive.get(f'{self.base_url}/{profile_id}/users', params=params)

    def remove(self, profile_id: str, user_id: str) -> None:
        """
        Remove the user from the profile.

        Only applicable to tenants using version 1 of profiles. If the tenant is on version 2 of profiles then use
        `britive.profiles.policies.*` instead.

        :param profile_id: The ID of the profile.
        :param user_id: The ID of the user.
        :return: None.
        """

        return self.britive.delete(f'{self.base_url}/{profile_id}/users/{user_id}')


class ProfileTags:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/paps'

    def add(self, profile_id: str, tag_id: str, start: datetime = None, end: datetime = None) -> dict:
        """
        Add a tag to the profile.

        Only applicable to tenants using version 1 of profiles. If the tenant is on version 2 of profiles then use
        `britive.profiles.policies.*` instead.

        :param profile_id: The ID of the profile.
        :param tag_id: The ID of the tag.
        :param start: The optional start time of when the association should be in effect. Providing start implies that
            end will also be provided. `start` will be interpreted as if in UTC timezone so it is up to the caller to
            ensure that the datetime object represents UTC. Not timezone manipulation will occur.
        :param end: The optional end time of when the association should be in effect. Providing end implies that start
            will also be provided. `end` will be interpreted as if in UTC timezone so it is up to the caller to
            ensure that the datetime object represents UTC. Not timezone manipulation will occur.
        :return: Details of added tag.
        """

        data = {}
        if start and end:
            data['start'] = start.isoformat(sep='T', timespec='seconds') + 'Z'
            data['end'] = end.isoformat(sep='T', timespec='seconds') + 'Z'

        return self.britive.post(f'{self.base_url}/{profile_id}/user-tags/{tag_id}', json=data)

    def list_assigned(self, profile_id: str, filter_expression: str = None) -> list:
        """
        List the tags assigned to the profile.

        Only applicable to tenants using version 1 of profiles. If the tenant is on version 2 of profiles then use
        `britive.profiles.policies.*` instead.

        :param profile_id: The ID of the profile.
        :param filter_expression: Can filter based on `name`, `status`, `integrity check`. Valid operators are `eq` and
            `co`. Example: name co "Dev Account"
        :return: List of tags assigned to the profile.
        """

        params = {
            'page': 0,
            'size': 100
        }

        if filter_expression:
            params['filter'] = filter_expression

        return self.britive.get(f'{self.base_url}/{profile_id}/user-tags', params=params)

    def list_available(self, profile_id: str) -> list:
        """
        List users available to be assigned to the profile.

        Only applicable to tenants using version 1 of profiles. If the tenant is on version 2 of profiles then use
        `britive.profiles.policies.*` instead.

        :param profile_id: The ID of the profile.
        :return: List of tags that are available to be assigned to the profile.
        """

        params = {
            'page': 0,
            'size': 100,
            'query': 'available'
        }
        return self.britive.get(f'{self.base_url}/{profile_id}/user-tags', params=params)

    def remove(self, profile_id: str, tag_id: str) -> None:
        """
        Remove the tag from the profile.

        Only applicable to tenants using version 1 of profiles. If the tenant is on version 2 of profiles then use
        `britive.profiles.policies.*` instead.

        :param profile_id: The ID of the profile.
        :param tag_id: The ID of the tag.
        :return: None.
        """

        return self.britive.delete(f'{self.base_url}/{profile_id}/user-tags/{tag_id}')


class ProfileSessionAttributes:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/paps'

    def add_static(self, profile_id: str, tag_name: str, tag_value: str, transitive: bool = False) -> dict:
        """
        AWS ONLY - Add a static session attribute to the profile.

        :param profile_id: The ID of the profile.
        :param tag_name: The name of the session tag to include in the AssumeRoleWithSAML call.
        :param tag_value: THe value of the session tag to include in the AssumeRoleWithSAML call.
        :param transitive: Set to True to mark the session tag as transitive. Review AWS documentation on why you
            may or may not want this.
        :return: Details of added attribute.
        """

        data = {
            'sessionAttributeType': 'Static',
            'transitive': transitive,
            'attributeSchemaId': None,
            'mappingName': tag_name,
            'attributeValue': tag_value
        }

        return self.britive.post(f'{self.base_url}/{profile_id}/session-attributes', json=data)

    def add_dynamic(self, profile_id: str, identity_attribute_id: str, tag_name: str,
                    transitive: bool = False) -> dict:
        """
        AWS ONLY - Add a dynamic session attribute to the profile.

        The value will be sourced from the identity attribute specified.

        :param profile_id: The ID of the profile.
        :param identity_attribute_id: The ID of the identity attribute.  Call `britive.identity_attributes.list()`
            for details on which attributes can be provided.
        :param tag_name: The name of the session tag to include in the AssumeRoleWithSAML call. The value will be
            dynamically determined based on the value of the specified identity attribute.
        :param transitive: Set to True to mark the session tag as transitive. Review AWS documentation on why you
            may or may not want this.
        :return: Details of added attribute.
        """

        data = {
            'sessionAttributeType': 'Identity',
            'transitive': transitive,
            'attributeSchemaId': identity_attribute_id,
            'mappingName': tag_name,
            'attributeValue': None
        }

        return self.britive.post(f'{self.base_url}/{profile_id}/session-attributes', json=data)

    def update_static(self, profile_id: str, attribute_id, tag_name: str, tag_value: str,
                      transitive: bool = False) -> None:
        """
        AWS ONLY - Update the static session attribute to the profile.

        :param profile_id: The ID of the profile.
        :param attribute_id: The ID of the session attribute to update.
        :param tag_name: The name of the session tag to include in the AssumeRoleWithSAML call.
        :param tag_value: THe value of the session tag to include in the AssumeRoleWithSAML call.
        :param transitive: Set to True to mark the session tag as transitive. Review AWS documentation on why you
            may or may not want this.
        :return: None.
        """

        data = {
            'sessionAttributeType': 'Static',
            'transitive': transitive,
            'attributeSchemaId': None,
            'mappingName': tag_name,
            'attributeValue': tag_value,
            'id': attribute_id
        }

        return self.britive.put(f'{self.base_url}/{profile_id}/session-attributes', json=data)

    def update_dynamic(self, profile_id: str, attribute_id: str, identity_attribute_id: str, tag_name: str,
                       transitive: bool = False) -> dict:
        """
        AWS ONLY - Update the dynamic session attribute to the profile.

        :param profile_id: The ID of the profile.
        :param attribute_id: The ID of the session attribute to update.
        :param identity_attribute_id: The ID of the identity attribute.  Call `britive.identity_attributes.list()`
            for details on which attributes can be provided.
        :param tag_name: The name of the session tag to include in the AssumeRoleWithSAML call. The value will be
            dynamically determined based on the value of the specified identity attribute.
        :param transitive: Set to True to mark the session tag as transitive. Review AWS documentation on why you
            may or may not want this.
        :return: Details of added attribute.
        """

        data = {
            'sessionAttributeType': 'Identity',
            'transitive': transitive,
            'attributeSchemaId': identity_attribute_id,
            'mappingName': tag_name,
            'attributeValue': None,
            'id': attribute_id
        }

        return self.britive.put(f'{self.base_url}/{profile_id}/session-attributes', json=data)

    def list(self, profile_id: str) -> list:
        """
        Return a list of session attributes associated with the profile.

        :param profile_id: The ID of the profile.
        :return: List of session attributes associated with the profile.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}/session-attributes')

    def remove(self, profile_id: str, attribute_id: str) -> None:
        """
        Remove an attribute from the profile.

        :param profile_id: The ID of the profile.
        :param attribute_id: The ID of the session attribute.
        :return: None.
        """

        return self.britive.delete(f'{self.base_url}/{profile_id}/session-attributes/{attribute_id}')


class ProfilePolicies:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/paps'

    def build(self, name: str, description: str = '', draft: bool = False, active: bool = True,
              read_only: bool = False, users: list = None, tags: list = None,
              service_identities: list = None, ips: list = None, from_time: str = None,
              to_time: str = None, approval_notification_medium: str = None, time_to_approve: int = 5,
              access_validity_time: int = 120, approver_users: list = None, approver_tags: list = None,
              access_type: str = 'Allow') -> dict:
        """
        Build a policy document that can be applied to a profile.

        :param name: The name of the policy.
        :param description: An optional description of the policy.
        :param draft: Indicates if the policy is a draft. Defaults to `False`.
        :param active: Indicates if the policy is a active. Defaults to `True`.
        :param read_only: Indicates if the policy is a read only. Defaults to `False`.
        :param users: Optional list of user names to which this policy applies.
        :param tags: Optional list of tag names to which this policy applies.
        :param service_identities: Optional list of service identity names to which this policy applies.
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

        policy = self.britive.policies.build(
            name=name,
            description=description,
            draft=draft,
            active=active,
            read_only=read_only,
            users=users,
            tags=tags,
            service_identities=service_identities,
            ips=ips,
            from_time=from_time,
            to_time=to_time,
            approval_notification_medium=approval_notification_medium,
            time_to_approve=time_to_approve,
            access_validity_time=access_validity_time,
            approver_users=approver_users,
            approver_tags=approver_tags,
            access_type=access_type
        )

        # clean up the generic policy response and customize for profiles
        policy.pop('permissions', None)
        policy.pop('roles', None)
        policy['consumer'] = 'papservice'

        return policy

    def list(self, profile_id: str) -> list:
        """
        List all policies associated with the provided profile.

        Only applicable to tenants using version 2 of profiles. If the tenant is on version 1 of profiles then use
        `britive.profiles.tags.*` and `britive.profiles.identities.*` instead.

        :param profile_id: The ID of the profile.
        :return: List of policies.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}/policies')

    def get(self, profile_id: str, policy_id: str) -> dict:
        """
        Retrieve details about a specific policy which is associated with the provided profile.

        Only applicable to tenants using version 2 of profiles. If the tenant is on version 1 of profiles then use
        `britive.profiles.tags.*` and `britive.profiles.identities.*` instead.

        :param profile_id: The ID of the profile.
        :param policy_id: The ID of the policy.
        "return: Details of the policy.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}/policies/{policy_id}')

    def create(self, profile_id: str, policy: dict) -> dict:
        """
        Create a policy associated with the provided profile.

        Only applicable to tenants using version 2 of profiles. If the tenant is on version 1 of profiles then use
        `britive.profiles.tags.*` and `britive.profiles.identities.*` instead.

        :param profile_id: The ID of the profile.
        :param policy: The policy contents to create.
        :return: Details of the newly created policy.
        """

        return self.britive.post(f'{self.base_url}/{profile_id}/policies', json=policy)

    def update(self, profile_id: str, policy_id: str, policy: dict) -> dict:
        """
        Update the contents of the provided policy associated with the provided profile.

        Only applicable to tenants using version 2 of profiles. If the tenant is on version 1 of profiles then use
        `britive.profiles.tags.*` and `britive.profiles.identities.*` instead.

        :param profile_id: The ID of the profile.
        :param policy_id: The ID of the policy.
        :param policy: The policy to update.
        :return: Details of the updated policy.
        """

        return self.britive.patch(f'{self.base_url}/{profile_id}/policies/{policy_id}', json=policy)

    def delete(self, profile_id: str, policy_id: str) -> None:
        """
        Delete the provided policy associated with the provided profile.

        Only applicable to tenants using version 2 of profiles. If the tenant is on version 1 of profiles then use
        `britive.profiles.tags.*` and `britive.profiles.identities.*` instead.

        :param profile_id: The ID of the profile.
        :param policy_id: The ID of the policy.
        :return: None.
        """

        return self.britive.delete(f'{self.base_url}/{profile_id}/policies/{policy_id}')
