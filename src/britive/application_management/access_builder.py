class AccessBuilderSettings:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

        self.approvers_groups = AccessBuilderApproversGroups(britive)
        self.associations = AccessBuilderAssociations(britive)
        self.notifications = AccessBuilderNotifications(britive)
        self.requesters = AccessBuilderRequesters(britive)

    def get(self, application_id: str) -> dict:
        """
        Get Access Request settings for an application

        :param application_id: The ID of the application to fetch Access Request settings.
        :return: dictionary of Access Request settings.
        """

        return self.britive.get(f'{self.base_url}/{application_id}/access-request-settings')

    def enable(self, application_id: str, approval_timeout: str = '00:06:00', expiration_timeout: int = 360) -> None:
        """
        Enable Access Requests for an application - at least 1 Association and 1 Notification Medium is required before
        enabling Access Requests for the application.

        :param application_id: The ID of the application to enable Access Requests
        :param approval_timeout: The time, in 'DD:HH:MM' format, for the approval timeout, default is '00:06:00'
        :param expiration_timeout: The time, in minutes, for the profile expiration timeout, default is 360
        :return: None
        """

        data = {
            'approvalTimeOut': approval_timeout,
            'profileExpirationTimeout': expiration_timeout,
            'allowAccessRequest': True,
        }
        return self.britive.patch(f'{self.base_url}/{application_id}/access-request-settings', json=data)

    def disable(self, application_id: str) -> None:
        """
        Disable Access Requests for application.

        :param application_id: The ID of the application to disable Access Requests
        :return: None
        """

        return self.britive.patch(
            f'{self.base_url}/{application_id}/access-request-settings', json={'allowAccessRequest': False}
        )


class AccessBuilderApproversGroups:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, application_id: str) -> list:
        """
        List Approvers Groups created for an application.

        :param application_id: The ID of the application to list Approvers Groups
        :return: List of Approvers Groups and their details
        """

        return self.britive.get(f'{self.base_url}/{application_id}/approvers-groups')

    def list_approvers_group_members(self, application_id: str, group_id: str) -> dict:
        """
        List Approvers Group members

        :param application_id: The ID of the application to which the Approvers Group is attached
        :param group_id: The ID of the Approvers Group to list members of
        :return: list of users and user tags that are members of the Approvers Group
        """

        return self.britive.get(f'{self.base_url}/{application_id}/approvers-groups/{group_id}')

    def create(self, application_id: str, name: str, condition: str, member_list: list = None) -> dict:
        """
        Create Approvers Group for Access Requests

        :param application_id: The ID of application to which the Approvers Group will be attached
        :param name: Name of the Approvers Group
        :param condition: One of [Any, Or]
        :param member_list: List of users and/or user tags
            Example: [
                {'id': user ID, 'memberType': 'User', ... other user attributes},
                {'id': tag ID, 'memberType': 'Tag', ... other tag attributes}
            ]
        :return: Dictionary of Approvers Group details
        """

        if member_list is None:
            member_list = []

        data = {'name': name, 'condition': condition, 'members': member_list}

        return self.britive.post(f'{self.base_url}/{application_id}/approvers-groups', json=data)

    def update(self, application_id: str, group_id: str, name: str, condition: str, member_list: list = None) -> dict:
        """
        Updates Approvers Group for given id

        :param application_id: The ID of the application
        :param group_id: Approvers Group ID to which the member list will be updated
        :param name: Name of the group
        :param condition: One of [Any, Or]
        :param member_list: This should be the final list of users and/or user tags you want attached to the group.
            Note: This list will overwrite what is already attached to the group.
            Example: [
                {'id': user ID, 'memberType': 'User', ... other user attributes},
                {'id': tag ID, 'memberType': 'Tag', ... other tag attributes}
            ]
        :return: dictionary of Approvers Group members
        """

        if member_list is None:
            member_list = []

        data = {'name': name, 'condition': condition, 'members': member_list}

        return self.britive.patch(f'{self.base_url}/{application_id}/approvers-groups/{group_id}', json=data)

    def delete(self, application_id: str, group_id: str) -> None:
        """
        Delete Approvers Group

        :param application_id: The ID of the application to which the Approvers Group is attached
        :param group_id: Id of the Approvers Group that needs to e deleted
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{application_id}/approvers-groups/{group_id}')


class AccessBuilderAssociations:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, application_id: str) -> dict:
        """
        List Associations and Approvers Groups combination configured for an application

        :param application_id: The ID of the application for which to list the Associations
        :return: dictionary of Associations and Approvers
        """

        return self.britive.get(f'{self.base_url}/{application_id}/association-approvers')

    def create(self, application_id: str, name: str, associations: list = None, approvers_groups: list = None) -> None:
        """
        Create Association Approvers

        :param application_id: The ID of application for which we are creating the Association Approvers
        :param name: Association name
        :param associations: list of associations
            Example: [
                {'type': (1 for environment group, 0 for environment),'id': ID of the environment or environment group},
                {'type': ..., 'id': ...},
            ]
        :param approvers_groups: list of Approvers Group IDs
            Example: [
                {'id': Approvers Group ID},
                {'id': Approvers Group ID},
            ]
        :return: None
        """

        data = {'name': name, 'associations': associations, 'approversGroups': approvers_groups}

        return self.britive.post(f'{self.base_url}/{application_id}/association-approvers', json=data)

    def get(self, application_id: str, association_id: str) -> dict:
        """
        Get configured association and approvers by id to an application

        :param application_id: The ID of application for which the Association is attached to
        :param association_id: The ID of the Association
        :return:
        """
        return self.britive.get(f'{self.base_url}/{application_id}/association-approvers/{association_id}')

    def update(
        self, application_id: str, association_id: str, associations: list = None, approvers_groups: list = None
    ) -> None:
        """
        Update Associations or Approvers Groups

        :param application_id: The ID of application for which we are updating the Association or Approvers Groups
        :param association_id: The ID of the Association to update
        :param associations: Leave blank if you do not want to update associations.
            list of associations you want to keep after the update
            Example: [
                {'type': (1 for environment group, 0 for environment),'id': ID of the environment or environment group},
                {'type': ..., 'id': ...},
            ]
        :param approvers_groups: Leave blank if you do not want to update approvers_groups.
            list of approvers_groups you want to keep after the update
            Example: [
                {'id': Approvers Group ID},
                {'id': Approvers Group ID},
            ]
        :return: None
        """

        data = {}

        if associations:
            data['associations'] = associations

        if approvers_groups:
            data['approversGroups'] = approvers_groups

        return self.britive.patch(f'{self.base_url}/{application_id}/association-approvers/{association_id}', json=data)

    def delete(self, application_id: str, association_id: str) -> None:
        """
        Delete the Association Approvers Group ID

        :param application_id: The ID of application for which the Association Approvers need to be deleted
        :param association_id: The ID of the Association of environments and Approvers Groups
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{application_id}/association-approvers/{association_id}')


class AccessBuilderNotifications:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, application_id: str) -> list:
        """
        List Access Requests Notification Mediums for an application

        :param application_id: The ID of application for which the notification mediums are attached to
        :return: List of notification mediums and their properties
        """

        settings = self.britive.get(f'{self.base_url}/{application_id}/access-request-settings')
        return settings.get('notificationMediums')

    def update(self, application_id: str, notification_mediums: list) -> None:
        """
        Update Access Requests Notification Mediums for an application

        :param application_id:
        :param notification_mediums: List of Notification Medium objects - this has to be the full list of mediums.
            Example: [
                {
                    'id': notification_medium.get('id'),
                    'name': notification_medium.get('name'),
                    'description': notification_medium.get('description'),
                    'application': notification_medium.get('type'),
                    'channels': notification_medium.get('channels', []),
                },
                {
                    'id': ... ,
                    'name': ... ,
                    'description': ... ,
                    'application': ... ,
                    'channels': ... ,
                },
                ...
            ]
        :return: None
        """

        data = {'notificationMediums': notification_mediums}

        return self.britive.patch(f'{self.base_url}/{application_id}/access-request-settings', json=data)


class AccessBuilderRequesters:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, application_id: str) -> list:
        """
        List users, tags who can use Access Builder for an applciation

        :param application_id: The ID of application for which the requesters need to be listed
        :return: List of members who can use access builder
        """

        settings = self.britive.get(f'{self.base_url}/{application_id}/access-request-settings')

        return settings.get('memberRules', [])

    def update(self, application_id: str, user_tag_members: list) -> None:
        """
        Update who can use Access Builder for an application

        :param application_id:
        :param user_tag_members: This should be the final list of users and/or user tags you want attached to the group.
            Note:
                1) This list will overwrite what is already attached to the application.
                2) condition key value should be either 'Include' or 'Exclude'
            Example: [
                {
                    'id': user ID,
                    'memberType': 'User',
                    'condition': 'Include' | 'Exclude',
                    ... other user attributes
                },
                {
                    'id': tag ID,
                    'memberType': 'Tag',
                    'condition': '',
                    ... other tag attributes
                },
            ]
        :return: None
        """

        data = {'memberRules': user_tag_members}

        return self.britive.patch(f'{self.base_url}/{application_id}/access-request-settings', json=data)


class AccessBuilderManagedPermissions:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/profile-requests/apps'

    def create(
        self,
        application_id: str,
        name: str,
        permissions: list,
        description: str = '',
        type: str = 'role',
        tags: list = None,
    ) -> dict:
        """
        Add managed permission to the application, from Access Builder.

        :param application_id: The ID of the application.
        :param name: The name of the new managed permission.
        :param permissions: The policies of the new managed permission.
        :param description: The description of the new managed permission.
        :param type: The type of the new managed permission.
        :param tags: The tags of the new managed permission.
        :return: Dict containing details of the new managed permission.
        """

        data = {
            'childPermissions': permissions,
            'description': description,
            'name': name,
            'tags': [] if tags is None else tags,
            'type': type,
        }

        return self.britive.get(f'{self.base_url}/{application_id}/britive-managed/permissions', json=data)

    def get(self, application_id: str, permission_id: str) -> dict:
        """
        Return details of the managed permission, from Access Builder.

        :param application_id: The ID of the application.
        :param permission_id: The ID of the managed permission.
        :return: Dict containing details of the managed permission.
        """

        return self.britive.get(f'{self.base_url}/{application_id}/britive-managed/permissions/{permission_id}')

    def validate_policy(self, application_id: str, policy: dict) -> dict:
        """
        Validate the provided permission policy, from Access Builder.

        :param application_id:
        :param policy: The policy, in JSON format, to validate.
        :return: Dict of findings.
        """

        return self.britive.post(f'{self.base_url}/{application_id}/britive-managed/permissions/validate', json=policy)

    def findings(self, application_id: str, permission_id: str) -> dict:
        """
        Permission and policy validation findings, from Access Builder.

        :param application_id: The ID of the application.
        :param permission_id: The ID of the managed permission.
        :return: Dict of findings.
        """

        return self.britive.get(
            f'{self.base_url}/{application_id}/britive-managed/permissions/{permission_id}/findings'
        )
