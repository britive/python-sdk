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

    def list_users_sessions(self, user_id: str) -> list:
        """
        Retrieve a list of the active sessions of a user

        :param user_id: The target user
        :return: The list of the user's active sessions
        """

        return self.britive.get(f'{self.base_url}/{user_id}')

    def checkin(self, user_id: str, profile_ids: list = None) -> None:
        """
        Checks in a user's session.

        :param user_id: The target user
        :param profile_id: The target profile that has been checked out
        :return: None
        """

        if not profile_ids:
            print('No profiles checked in due to empty profile_ids')
        else:
            sessions = self.britive.get(f'{self.base_url}/{user_id}')
            target = None
            for item in sessions:
                if item['papId'] in profile_ids:
                    target = item['transactionId']
                    self.britive.delete(f'{self.base_url}/{target}')
