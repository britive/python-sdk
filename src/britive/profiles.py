from . import exceptions
import datetime

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
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'
        self.permissions = ProfilePermissions(britive)
        self.identities = ProfileIdentities(britive)
        self.tags = ProfileTags(britive)
        self.session_attributes = ProfileSessionAttributes(britive)

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

    def update_dynamic(self, profile_id: str, attribute_id:str, identity_attribute_id: str, tag_name: str,
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
