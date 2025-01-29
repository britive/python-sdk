class Vaults:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager/vault'

    def list(self) -> list:
        """
        Provide a list of all vaults.

        :return: List of all vaults
        """

        params = {'getmetadata': 'true'}
        return self.britive.get(self.base_url, params=params)

    def get_vault_by_id(self, vault_id: str) -> dict:
        """
        Provide details of the given vault, from a vault id.

        :param vault_id: The ID  of the vault.
        :return: Details of the specified vault.
        """

        return self.britive.get(f'{self.base_url}/{vault_id}')

    def create(
        self,
        name: str,
        description: str = 'Default vault description',
        rotation_time: int = 30,
        encryption_algorithm: str = 'AES_256',
        default_notification_medium_id: str = '',
        users: list = None,
        tags: list = None,
        channels: list = None,
    ) -> dict:
        """
        Create a new vault.

        :param name: the name of the vault
        :param description: the description of the vault
        :param rotation_time: in hours, how often the vault should rotate keys
        :param encryption_algorithm : the encryption algorithm to use for the vault
        :param default_notification_medium_id : the default notification medium to use for the vault
        :param users: a list of user IDs to recieve notifications for the vault
        :param tags: a list of tags to recieve notifications for the vault
        :param channels : a list of channels to recieve notifications for the vault (only for slack)
        :return: Details of the newly created vault.
        """

        if users is None:
            users = []
        if tags is None:
            tags = []
        if channels is None:
            channels = []

        if default_notification_medium_id == '':
            for medium in self.britive.global_settings.notification_mediums.list():
                if medium['name'] == 'Email':
                    default_notification_medium_id = medium['id']
        params = {
            'name': name,
            'description': description,
            'rotationTime': rotation_time,
            'encryptionAlgorithm': encryption_algorithm,
            'defaultNotificationMediumId': default_notification_medium_id,
            'recipients': {'userIds': users, 'tags': tags, 'channelIds': channels},
        }
        return self.britive.post(self.base_url, json=params)

    def delete(self, vault_id: str) -> None:
        """
        Deletes a vault.

        :param vault_id: the ID of the vault
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{vault_id}')

    def update(self, vault_id: str, **kwargs) -> None:
        """
        Updates a vault.

        If not all kwargs a provided, the vault will update with the default values of the unprovided kwargs.

        :param vault_id: The ID of the vault.
        :param kwargs: Valid fields are...
            name - required
            description
            rotationTime - time in days between key rotations
            encryptionAlgorithm - the encryption algorithm to use for the vault
            defaultNotificationMediumId - the default notification medium to use for the vault
            recipients - a list of user IDs or tags to recieve notifications for the vault
        :return: None
        """

        return self.britive.patch(f'{self.base_url}/{vault_id}', json=kwargs)

    def rotate_keys(self) -> None:
        """
        Rotate vault keys.

        :return: None
        """

        return self.britive.post(f'{self.britive.base_url}/v1/secretmanager/keys/rotate')
