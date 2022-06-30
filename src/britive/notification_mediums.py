class NotificationMediums:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/notification-service/notificationmediums'
    def list(self):
        """
        Provide a list of all notification mediums 
        :return: List of all notification mediums
        """
        return self.britive.get(self.base_url)

    def create(self, type : str, name : str, description : str = "Default notification medium description", connectionParameters : dict = {}) -> dict:
        """
        Create a new notification medium.
        :param 
            type : the type of the notification medium
            name : the name of the notification medium
            description : the description of the notification medium
            connectionParameters : the connection parameters of the notification medium
                valid connection parameters: 
                    URL : for slack, the URL
                    token : for slack, Auth Token for the Application BOT
                    Webhook URL : for teams, the URL of the teams webhook
        :return: Details of the newly created notification medium.
        """
        params = {'name': name, 'description': description, 'type': type, 'connectionParameters': connectionParameters}
        return(self.britive.post(self.base_url, json=params))
    def get(self, notification_medium_id):
        """
        Provide details of the given notification medium, from a notification medium id.
        :param notification_medium_id: The ID  of the notification medium.
        :return: Details of the specified notification medium.
        """
        return self.britive.get(f'{self.base_url}/{notification_medium_id}')
    def update(self, notification_medium_id : str, **kwargs):
        """
        Update a notification medium.
        :param ID: The ID of the notification medium.
        :param kwargs: Valid fields are...
            name : the name of the notification medium
            description : the description of the notification medium
            connectionParameters : the connection parameters of the notification medium
                valid connection parameters: 
                    URL : for slack, the URL
                    token : for slack, Auth Token for the Application BOT
                    Webhook URL : for teams, the URL of the teams webhook
        :return: Details of the updated notification medium.
        """
        creation_defaults = self.get(notification_medium_id)
        data = {**creation_defaults, **kwargs}
        return(self.britive.patch(f'{self.base_url}/{notification_medium_id}', json=data))
    def delete(self, notification_medium_id: str):
        """
        Deletes a notification medium.
        :param notification_medium_id: the ID of the notification medium
        :return: none
        """
        return self.britive.delete(f'{self.base_url}/{notification_medium_id}')
    def get_channels(self, notification_medium_id: str):
        """
        Provide a list of all channels for the given notification medium (only for slack).
        :param notification_medium_id: The ID of the notification medium.
        :return: List of all channels for the given notification medium.
        """
        return self.britive.get(f'{self.base_url}/{notification_medium_id}/channels')