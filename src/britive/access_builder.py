import json

enable_defaults = {
    'approvalTimeOut': '00:06:00',
    'profileExpirationTimeout': 360
}

class AccessBuilderSettings:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

        self.approvers_groups = AccessBuilderApproverGroups(britive)
        self.associations = AccessBuilderAssociation(britive)
        self.notifications = AccessBuilderNotifications(britive)
        self.requesters = AccessBuilderRequesters(britive)

    def get(self, application_id: str) -> dict:
        """
        Get Access Request settings for application

        :param application_id: The ID of the application to fetch access request settings.
        :return: dictionary of access request settings.
        """
        return self.britive.get(f'{self.base_url}/{application_id}/access-request-settings')

    def enable(self, application_id: str, **kwargs) -> None:
        """
        Enable access requests for application. At least 1 Association and 1 Notification medium is required
            before enabling access requests for the application.

        :param application_id: The ID of the application to enable access requests
        :param kwargs: in json format with values for the keys approvalTimeOut and
            profileExpirationTimeout.
            approvalTimeOut:str time in format 'DD:HH:MM'
            profileExpirationTimeout:int time in minutes
        :return: None
        """

        data = {**enable_defaults, **kwargs, 'allowAccessRequest': True}
        return self.britive.patch(f'{self.base_url}/{application_id}/access-request-settings'
                                  , json=data)

    def disable(self, application_id: str) -> None:
        """
        disable access requests for application.

        :param application_id: The ID of the application to disable access requests
        :return: None
        """
        data = {'allowAccessRequest': False}
        return self.britive.patch(f'{self.base_url}/{application_id}/access-request-settings'
                                  , json=data)


class AccessBuilderApproverGroups:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, application_id: str) -> list:
        """
        List approver groups created for an application.

        :param application_id: The ID of the application to list approver groups
        :return: List of approver groups and their details
        """
        return self.britive.get(f'{self.base_url}/{application_id}/approvers-groups')

    def list_approver_group_members(self, application_id: str, approver_group_id: str) -> dict:
        """
        List approver group members

        :param application_id: The ID of the application to which the approver group is attached
        :param approver_group_id: The ID of the approver group to list members of
        :return: list of users and user tags that are members of the approver group
        """

        return self.britive.get(f'{self.base_url}/{application_id}/approvers-groups/{approver_group_id}')

    def create(self, application_id: str, name: str, condition: str
               , member_list: list = None) -> dict:
        """
        Create approver group for access requests

        :param application_id: The ID of application to which the approver group will be attached
        :param name: Name of the approver group
        :param condition: One of [Any, Or]
        :param member_list: List of users and/or user tags
            [{'id': user ID, 'memberType': 'User', ..... other user attributes}
            , {'id': tag ID, 'memberType': 'Tag', ....... other tag attributes}]
        :return: Dictionary of approver group details
        """

        data = {'name': name,
                'condition': condition,
                'members': member_list}

        return self.britive.post(f'{self.base_url}/{application_id}/approvers-groups'
                                 , json=data)

    def update(self, application_id: str, approver_group_id: str
               , name: str, condition: str, member_list: list = []) -> dict:
        """

        :param application_id: The ID of the application
        :param name: Name of the approver group
        :param condition: One of [Any, Or]
        :param member_list: This should be the final list of users and/or user tags you want attached to the group.
            Note: This list will overwrite what is already attached to the group.
                [{'id': user ID, 'memberType': 'User', ..... other user attributes}
                , {'id': tag ID, 'memberType': 'Tag', ....... other tag attributes}]
        :param approver_group_id: Approver group ID to which the member list will be updated
        :return: dictionary of approver group members
        """

        data = {'name': name,
                'condition': condition,
                'members': member_list}

        return self.britive.patch(f'{self.base_url}/{application_id}/approvers-groups/{approver_group_id}'
                                  , json=data)

    def delete(self, application_id: str, approver_group_id: str) -> None:
        """
        Delete approver group

        :param application_id: The ID of the application to which the approver group is attached
        :param approver_group_id: Id of the approver group that needs to e deleted
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{application_id}/approvers-groups/{approver_group_id}')


class AccessBuilderAssociation:

    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, application_id: str) -> dict:
        """
        List associations and approvers attached to the application ID

        :param application_id: The ID of the application for which to list the associations
        :return: dictionary of associations and approvers
        """
        return self.britive.get(f'{self.base_url}/{application_id}/association-approvers')

    def create(self, application_id: str, name: str
               , associations: list = None, approvers_groups: list = None) -> None:
        """
        Create association approvers

        :param application_id: The ID of application for which we are creating the association approvers
        :param name: Association name
        :param associations: list of associations
            [   {'type': (1 for environment group, 0 for environment)
                        , 'id': nativeID of the environment or environment group}
                , {'type': ......, 'id':}
                , {'type': ......, 'id':}
            ]
        :param approvers_groups: list of approver group IDs
            [ {'id': approver group ID}
                , {'id': approver group ID}
                ,
            ]
        :return: None
        """
        data = {'name': name
            , 'associations': associations
            , 'approversGroups': approvers_groups
                }

        return self.britive.post(f'{self.base_url}/{application_id}/association-approvers'
                                 , json=data)

    def get(self, application_id: str, association_id: str) -> dict:
        """
        :param application_id: The ID of application for which the association is attached to
        :param association_id: The ID of the association
        :return:
        """
        return self.britive.get(f'{self.base_url}/{application_id}/association-approvers/{association_id}')

    def update(self, application_id: str, association_id: str
               , associations: list = [], approvers_groups: list = []) -> None:
        """
        Update assocations or approvers

        :param application_id: The ID of application for which we are updating the association approvers
        :param association_id: The ID of the Association to update
        :param associations: Leave blank if you do not want to update associations.
            list of associations you want to keep after the update
            [   {'type': (1 for environment group, 0 for environment)
                        , 'id': nativeID of the environment or environment group}
                , {'type': ......, 'id':}
                , {'type': ......, 'id':}
            ]
        :param approvers_groups: Leave blank if you do not want to update approvers_groups.
            list of approvers_groups you want to keep after the update
            [ {'id': approver group ID}
                , {'id': approver group ID}
                ,
            ]
        :return: None
        """

        data = {}

        if len(associations) > 0:
            data['associations'] = associations

        if len(approvers_groups) > 0:
            data['approversGroups'] = approvers_groups

        return self.britive.patch(f'{self.base_url}/{application_id}/association-approvers/{association_id}'
                                  , json=data)

    def delete(self, application_id: str, association_id: str) -> None:
        """
        Delete the association approver group ID

        :param application_id: The ID of application for which the association approvers need to be deleted
        :param association_id: The ID of the association of environments and approver groups
        :return: None
        """
        return self.britive.delete(f'{self.base_url}/{application_id}/association-approvers/{association_id}')


class AccessBuilderNotifications:

    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, application_id: str) -> list:
        """
        List Notification mediums attached to the access requests

        :param application_id: The ID of application for which the notification mediums are attached to
        :return: List of notification mediums and their properties
        """
        settings = self.britive.get(f'{self.base_url}/{application_id}/access-request-settings')
        return settings.get('notificationMediums')

    def update(self, application_id: str, notification_medium: list) -> None:
        """
        :param application_id:
        :param notification_medium: List of notification medium object formatted as below. This has to be the full list
            of mediums.
            notification medium object format:
                {'id': notification_medium.get('id')
                    , 'name': notification_medium.get('name')
                    , 'description': notification_medium.get('description')
                    , 'application': notification_medium.get('type')
                    , 'channels': notification_medium.get('channels', [])
                    , 'connectionParameters' : notification_medium.get('connectionParameters', {})}

        :return: None
        """

        data = {'notificationMediums': notification_medium}

        return self.britive.patch(f'{self.base_url}/{application_id}/access-request-settings'
                                  , json=data)


class AccessBuilderRequesters:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'

    def list(self, application_id: str) -> list:
        """
        List users, tags who can use access builder

        :param application_id: The ID of application for which the requesters need to be listed
        :return: List of members who can use access builder
        """
        settings = self.britive.get(f'{self.base_url}/{application_id}/access-request-settings')
        return settings.get('memberRules')

    def update(self, application_id: str, user_tag_members: list) -> None:
        """

        :param application_id:
        :param user_tag_members: This should be the final list of users and/or user tags you want attached to the group.
            Note: 1) This list will overwrite what is already attached to the application.
                  2) condition key value should be one of 'Include' or 'Exclude'
                [{'id': user ID, 'memberType': 'User'
                        , 'condition': (should be one of 'Include' or 'Exclude'),  ..... other user attributes}
                , {'id': tag ID, 'memberType': 'Tag', 'condition': '',  ....... other tag attributes}]
        :return: None
        """

        data = {'memberRules': user_tag_members}

        return self.britive.patch(f'{self.base_url}/{application_id}/access-request-settings'
                                  , json=data)
