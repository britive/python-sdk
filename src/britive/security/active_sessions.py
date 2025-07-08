class ActiveSessions:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/paps/sessions'

    def list_users(self) -> list:
        """
        Retrieve a list of the users with active sessions

        :return: list of users
        """

        return self.britive.get(self.base_url)

    def list(self, user_id: str) -> list:
        """
        Retrieve a list of the active sessions of a user

        :param user_id: The target user
        :return: The list of the user's active sessions
        """

        return self.britive.get(f'{self.base_url}/{user_id}')

    def delete(self, user_id: str, profile_id: str) -> None:
        """
        Kills a user's session.

        :param user_id: The target user
        :param profile_id: The target profile that has been checked out
        :return: None
        """

        sessions = self.britive.get(f'{self.base_url}/{user_id}')
        target = None

        for item in sessions:
            if item['papId'] == profile_id:
                target = item['transactionId']
                self.britive.delete(f'{self.base_url}/{target}')

    def delete_all(self) -> None:
        """
        Kills all users' sessions

        :return: None
        """

        users = self.britive.get(self.base_url)
        total_sessions = []

        for user in users:
            user_id = user['userId']
            sessions = self.britive.get(f'{self.base_url}/{user_id}')
            for session in sessions:
                total_sessions.append(session)

        for item in total_sessions:
            target = item['transactionId']
            self.britive.delete(f'{self.base_url}/{target}')
