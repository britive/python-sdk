class NotificationMediums:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/notification-service/notificationmediums'

    def list(self, filter_expression: str = None) -> dict:
        """
        List all notification mediums.

        :param filter_expression: Filter based on `name`. Example: `name co britive`.
        :return: List of all notification mediums
        """

        params = {}

        if filter_expression:
            params['filter'] = filter_expression

        return self.britive.get(self.base_url, params=params)['result']

    def create(
        self,
        notification_medium_type: str,
        name: str,
        url: str,
        token: str = None,
        description: str = None,
    ) -> dict:
        """
        Create a new notification medium.

        :param notification_medium_type: the type of the notification medium - [slack, teams, webhook]
        :param name: the name of the notification medium
        :param url: the notification medium target URL
        :param token: **slack only** the Auth Token for the Application BOT
        :param description: the description of the notification medium
        :return: Details of the newly created notification medium.
        """

        if description is None:
            description = f'notification medium - {notification_medium_type}'

        connection_parameters = {
            **({'URL': url} if notification_medium_type != 'teams' else {'Webhook URL': url}),
            **({'token': token} if notification_medium_type == 'slack' and token else {}),
        }

        params = {
            'name': name,
            'description': description,
            'type': notification_medium_type,
            'connectionParameters': connection_parameters,
        }
        return self.britive.post(self.base_url, json=params)

    def get(self, notification_medium_id) -> dict:
        """
        Provide details of the given notification medium, from a notification medium id.

        :param notification_medium_id: The ID  of the notification medium.
        :return: Details of the specified notification medium.
        """

        return self.britive.get(f'{self.base_url}/{notification_medium_id}')

    def update(self, notification_medium_id: str, parameters: dict) -> dict:
        """
        Update a notification medium.

        :param notification_medium_id: The ID of the notification medium.
        :param parameters: Parameters to update, valid fields are...
            name: the name of the notification medium
            description: the description of the notification medium
            connectionParameters: the connection parameters of the notification medium
                valid connection parameters:
                    URL: for slack, the URL
                    token: for slack, Auth Token for the Application BOT
                    Webhook URL: for teams, the URL of the teams webhook
        :return: Details of the updated notification medium.
        """

        return self.britive.patch(f'{self.base_url}/{notification_medium_id}', json=parameters)

    def delete(self, notification_medium_id: str) -> None:
        """
        Deletes a notification medium.

        :param notification_medium_id: the ID of the notification medium
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{notification_medium_id}')

    def get_channels(self, notification_medium_id: str) -> dict:
        """
        Provide a list of all channels for the given notification medium (only for slack).

        :param notification_medium_id: The ID of the notification medium.
        :return: List of all channels for the given notification medium.
        """

        return self.britive.get(f'{self.base_url}/{notification_medium_id}/channels')
