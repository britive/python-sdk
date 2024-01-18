class Notifications:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/notifications'

    def list(self) -> list:
        """
        List notifications.

        :return: List of notifications.
        """

        return self.britive.get(self.base_url)

    def get(self, notification_id: str) -> dict:
        """
        Retrieve details about a notification.

        :param notification_id: The ID of the notification.
        :return: Details of the notification
        """

        return self.britive.get(f'{self.base_url}/{notification_id}')

    def create(self, name: str, description: str = None) -> dict:
        """
        Create a new notification.

        :param name: The name of the notification.
        :param description: An optional description of the notification.
        :return: Details of the newly created notification.
        """

        data = {
            'name': name,
            'description': description or ''
        }
        return self.britive.post(self.base_url, json=data)

    def update(self, notification_id: str, name: str = None, description: str = None) -> dict:
        """
        Update specific attributes of a notification.

        :param notification_id: The ID of the notification.
        :param name: The optional new name of the notification. Omitting will leave the name unchanged.
        :param description: The optional new description of the notification. Omitting will leave the description
            unchanged.
        :return: Details of the updated notification.
        """

        base = self.get(notification_id=notification_id)
        if name:
            base['name'] = name
        if description:
            base['description'] = description
        return self.britive.put(self.base_url, json=base)

    def available_rules(self) -> list:
        """
        List all supported notification rules.

        :return: List of notification rules which can be used to craft the events on which to notify.
        """

        return self.britive.get(f'{self.base_url}/supported-rules')

    def available_users(self, notification_id: str) -> list:
        """
        Provide list of available users which can be added to the notification.

        :param notification_id: The ID of the notification.
        :return: List of available users for the notification.
        """

        return self.britive.get(f'{self.base_url}/{notification_id}/available-users')

    def available_user_tags(self, notification_id: str) -> list:
        """
        Provide list of available user tags which can be added to the notification.

        :param notification_id: The ID of the notification.
        :return: List of available user tags for the notification.
        """

        return self.britive.get(f'{self.base_url}/{notification_id}/available-user-tags')

    def available_applications(self, notification_id: str) -> list:
        """
        Provide list of available applications which can be added to the notification.

        :param notification_id: The ID of the notification.
        :return: List of available applications for the notification.
        """

        return self.britive.get(f'{self.base_url}/{notification_id}/available-apps')

    def configure(self, notification_id: str, rules: list = None, users: list = None, user_tags: list = None,
                  applications: list = None, send_no_changes: bool = None, notification_medium_id: str = None) -> dict:
        """
        Configure the details of a notification.

        For all optional parameters omitting the parameter will leave the value unchanged.

        :param notification_id: The ID of the notification.
        :param rules: List of rules to apply. Obtain rule options from `britive.notifications.available_rules()` and
            use results from that API call to populate this list. Maximum of 3 rules are allowed.
        :param users: List of user ids to apply. This is the list of users who will be notified if any of the rules are
            triggered. An empty list means that no users will be notified.
        :param user_tags: List of user tag ids to apply. This is the list of user tags who will be notified if any of
            the rules are triggered. An empty list means that no user tags will be notified.
        :param applications: List of applications to which this notification applies. Obtain applications options from
            `britive.notifications.available_applications()` and use results from that API call to populate this list.
            An empty list indicates the event applies to all applications.
        :param send_no_changes: Boolean indicating whether to send notification regardless of whether any changes have
            occurred or not.
        :param notification_medium_id: The ID of the notification medium to use for this notification.
        :return: Details of the newly updated notification.
        """

        # some basic validation
        if rules and len(rules) > 3:
            raise ValueError('The maximum number of rules for a notification is 3.')

        # start with the existing notification details
        data = self.get(notification_id=notification_id)

        members = []
        for user in self.britive.users.minimized_user_details(user_ids=users):
            members.append(
                {
                    'id': user['id'],
                    'memberType': 'User',
                    'name': user['username'],
                    'condition': None
                }
            )

        for tag in self.britive.tags.minimized_tag_details(tag_ids=user_tags):
            members.append(
                {
                    'id': tag['userTagId'],
                    'memberType': 'Tag',
                    'name': tag['name'],
                    'condition': None
                }
            )

        # set the possible parameters
        params = {
            'rules': rules,
            'memberRules': members,
            'applications': applications,
            'sendNoChanges': send_no_changes,
            'notificationMedium': notification_medium_id
        }

        # fo each parameter update the existing notification data if the parameter was provided
        for key, value in params.items():
            if value:
                data[key] = value

        return self.britive.put(self.base_url, json=data)

    def disable(self, notification_id: str) -> dict:
        """
        Disable a notification.

        :param notification_id: The ID of the notification.
        :return: Details of the newly disabled notification.
        """

        return self.britive.post(f'{self.base_url}/{notification_id}/disabled-statuses')

    def enable(self, notification_id: str) -> dict:
        """
        Enable a notification.

        :param notification_id: The ID of the notification.
        :return: Details of the newly enabled notification.
        """

        return self.britive.post(f'{self.base_url}/{notification_id}/enabled-statuses')

    def delete(self, notification_id: str) -> None:
        """
        Delete a notification.

        :param notification_id: The ID of the notification.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{notification_id}')
