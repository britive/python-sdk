class ActiveSessions:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_urls = {
            'applications': f'{self.britive.base_url}/paps/sessions',
            'resources': f'{self.britive.base_url}/resource-manager/sessions',
        }

    def list_users(self, search_text: str = None) -> list:
        """
        Retrieve a list of users with active session(s), i.e. checked out profiles.

        :return: List of users with active session(s).
        """

        params = {}

        if search_text:
            params['searchText'] = search_text

        return self.britive.get(self.base_urls['applications'], params=params)

    def list_user_sessions(self, user_id: str) -> dict:
        """
        Retrieve the active sessions (checked out profiles) of a given user.

        :param user_id: The target user's ID.
        :return: Dict of the user's active Application and Resources sessions.
        """

        return {
            'applications': self.britive.get(f'{self.base_urls["applications"]}/{user_id}'),
            'resources': self.britive.get(f'{self.base_urls["resources"]}/{user_id}'),
        }

    def checkin(self, user_id: str, profile_ids: list) -> None:
        """
        Checkin one or more active profile sessions for a given user.

        :param user_id: The target user's ID.
        :param profile_ids: List of target profile ID(s) to checkin.
        :return: None
        """
        for transaction_id, profile_type in {
            session['transactionId']: profile_type
            for profile_type, sessions in self.list_user_sessions(user_id).items()
            for session in sessions
            if session.get('papId', session.get('profileId')) in profile_ids
        }.items():
            self.britive.delete(f'{self.base_urls[profile_type]}/{transaction_id}')

    def checkin_all(self, user_id: str) -> None:
        """
        Checkin all active profiles sessions for a given user.

        :param user_id: The target user's ID
        :return: None
        """

        self.britive.delete(f'{self.base_urls["applications"]}/user/{user_id}')
        self.britive.delete(f'{self.base_urls["resources"]}/checkin-all/{user_id}')
