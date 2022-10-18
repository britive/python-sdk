class NotificationMediums:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = (
            f'{self.britive.base_url}/v1/notification-service/notificationmediums'
        )

    def list(self) -> dict:
        """
        List all notification mediums.

        :return: List of all notification mediums
        """

        return self.britive.get(self.base_url)['result']

    def create(
        self,
        notification_medium_type: str,
        name: str,
        description: str = 'Default notification medium description',
        connection_parameters: dict = {}
    ) -> dict:
        """
        Create a new notification medium.

        :param notification_medium_type: the type of the notification medium
        :param name: the name of the notification medium
        :param description: the description of the notification medium
        :param connection_parameters: the connection parameters of the notification medium
                valid connection parameters:
                    URL : for slack, the URL
                    token : for slack, Auth Token for the Application BOT
                    Webhook URL : for teams, the URL of the teams webhook
        :return: Details of the newly created notification medium.
        """

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

        return self.britive.patch(
            f'{self.base_url}/{notification_medium_id}', json=parameters
        )

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
