class SecretsManager:
    def __init__(self, britive):
        self.vaults = Vaults(britive)

class Vaults():
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager/vault'

    def list(self) -> list:
        """
        Provide a list of all vaults 

        :return: List of all vaults
        """
        params = {
            'getmetadata': 'true'
        }
        return self.britive.get(self.base_url, params=params)

    def get_vault_by_id(self, vault_id : str):
        """
        Provide details of the given vault, from a vault id.

        :param vault_id: The ID  of the vault.
        :return: Details of the specified vault.
        """
        return self.britive.get(f'{self.base_url}/{vault_id}')

    def create(self, name : str, description : str = "Default vault description", rotationTime : int = 30, encryptionAlgorithm : str = "AES_256", defaultNotificationMediumId : str = "", users : list = [], tags : list = [], channels : list = []) -> dict:

        """
        Create a new vault.

        :param 
            name : the name of the vault
            description : the description of the vault
            rotationTime : in hours, how often the vault should rotate keys
            encryptionAlgorithm : the encryption algorithm to use for the vault
            defaultNotificationMediumId : the default notification medium to use for the vault
            users : a list of user IDs to recieve notifications for the vault
            tags : a list of tags to recieve notifications for the vault
            channels : a list of channels to recieve notifications for the vault (only for slack)
        :return: Details of the newly created vault.
        """
        if(defaultNotificationMediumId == ""):
            for medium in self.britive.notification_mediums.list():
                if medium['name'] == 'Email':
                    defaultNotificationMediumId = medium['id']
        params = {'name': name, 'description': description, 'rotationTime': rotationTime, 'encryptionAlgorithm': encryptionAlgorithm, 'defaultNotificationMediumId': defaultNotificationMediumId, 'recipients' : {'userIds': users, 'tags': tags, 'channelIds': channels}}
        return(self.britive.post(self.base_url, json=params))
    
    def delete(self, vault_id: str):
        """
        Deletes a vault.

        :param vault_id: the ID of the vault

        :return: none
        """
        return self.britive.delete(f'{self.base_url}/{vault_id}')
    
    def update(self, vault_id : str, **kwargs):
        """
        Updates a vault. If not all kwargs a provided, the vault will update with the default values of the unprovided kwargs

        :param kwargs: Valid fields are...
            name - required
            description
            rotationTime
            encryptionAlgorithm
            defaultNotificationMediumId
            recipients


        :return: none
        """
        creation_defaults = self.get_vault_by_id(vault_id)
        data = {**creation_defaults, **kwargs}
        return self.britive.patch(f'{self.base_url}/{vault_id}', json=data)

    def rotate_keys(self):
        """
        Rotate vault keys

        :param: none

        :return: none
        """
        return self.britive.post(f'{self.britive.base_url}/v1/secretmanager/keys/rotate')