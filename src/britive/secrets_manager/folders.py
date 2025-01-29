class Folders:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager/vault'

    def create(self, name: str, vault_id: str, path: str = '/') -> dict:
        """
        Creates a new folder in the vault.

        :param name: The name of the folder.
        :param vault_id: The ID of the vault.
        :param path: The path of the folder (include the  leading /).
        :return: Details of the newly created folder.
        """

        data = {'entityType': 'node', 'name': name}
        return self.britive.post(f'{self.base_url}/{vault_id}/secrets?path={path}', json=data)

    def delete(self, vault_id: str, path: str) -> None:
        """
        Deletes a folder from the vault.

        :param vault_id: ID of the vault to delete the folder from
        :param path: path of the folder, include the / at the beginning
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{vault_id}/secrets?path={path}')
