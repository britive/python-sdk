import json


class Secrets:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager/vault'

    def create(
        self,
        name: str,
        vault_id: str,
        description: str = '',
        file: bytes = None,
        path: str = '/',
        secret_mode: str = 'shared',
        secret_nature: str = 'static',
        static_secret_template_id: str = '7a5f41d8-f7af-46a0-88f7-edf0403607ae',
        value: dict = None,
    ) -> dict:
        """
        Creates a new secret in the vault.

        For creating a secret with a file, you must read the file in with:
            with open(file_path, 'rb') as f:
                britive.secrets_manager.secrets.create(...., file=f)


        :param name: name of the secret
        :param vault_id: ID of the vault
        :param path: path of the secret, include the / the beginning
        :param static_secret_template_id: ID of the static secret template
        :param secret_mode: mode of the secret
        :param secret_nature: nature of the secret
        :param value: value of the secret (must be in the format of the static secret template)
        :param file: file to upload as the secret
        :return: Details of the newly created secret.
        """
        if value is None:
            value = {'Note': 'This is the default note'}

        if not file:
            return self.britive.post(
                f'{self.base_url}/{vault_id}/secrets?path={path}',
                json={
                    'description': description,
                    'entityType': 'secret',
                    'name': name,
                    'secretMode': secret_mode,
                    'secretNature': secret_nature,
                    'staticSecretTemplateId': static_secret_template_id,
                    'value': value,
                },
            )
        secret_data = {
            'description': description,
            'entityType': 'secret',
            'name': name,
            'secretMode': secret_mode,
            'secretNature': secret_nature,
            'staticSecretTemplateId': static_secret_template_id,
            'value': value,
        }
        return self.britive.post_upload(
            f'{self.base_url}/{vault_id}/secrets/file?path={path}',
            files={'file': file, 'secretData': (None, json.dumps(secret_data))},
        )

    def update(
        self,
        vault_id: str,
        path: str = '/',
        name: str = None,
        description: str = None,
        value: dict = None,
        file: bytes = None,
    ) -> None:
        """
        Updates a secret's value

        :param vault_id: ID of the vault to update the secret in
        :param path: path of the secret, include the / at the beginning
        :param value: value of the secret
        :param file: file to upload as the secret
        :return: None
        """
        secret_data = {
            **({'description': description} if description else {}),
            **({'name': name} if name else {}),
        }
        if value:
            return self.britive.patch(
                f'{self.base_url}/{vault_id}/secrets?path={path}',
                json={**secret_data, **{'value': value}},
            )
        if file:
            return self.britive.patch(
                f'{self.base_url}/{vault_id}/secrets/file?path={path}',
                files={'file': file, 'secretData': (None, json.dumps(secret_data))},
            )
        return None

    def rename(self, vault_id: str, path: str = '/', new_name: str = '') -> None:
        """
        Update the name of a secret.

        :param vault_id: ID of the vault to update the secret in
        :param path: path of the secret, include the / at the beginning and the secret name
        :param new_name: new name of the secret
        :return: None
        """

        return self.britive.patch(f'{self.base_url}/{vault_id}/secrets?path={path}', json={'name': new_name})

    def get(
        self,
        vault_id: str,
        path: str,
        secret_type: str = 'node',
        filter_type: str = None,
        recursive_secrets: bool = False,
        get_metadata: bool = True,
    ) -> dict:
        """
        Gets a secret from the vault.

        :param vault_id: ID of the vault to get the secret from
        :param path: path of the secret, include the / at the beginning
        :param secret_type: type of the secret (node or secret)
        :param filter_type: filter to apply to the secret (NONE, ALL, SHARED, PRIVATE)
        :param recursive_secrets: whether or not to recursively get all secrets in the folder
        :param get_metadata: whether or not to get the metadata of the secret
        :return: Details of the secret.
        """

        params = {
            'type': secret_type,
            'filter': filter_type,
            'recursiveSecrets': (str(recursive_secrets)).lower(),
            'getMetadata': get_metadata,
        }
        return self.britive.get(f'{self.base_url}/{vault_id}/secrets?path={path}', params=params)

    def delete(self, vault_id: str, path: str) -> None:
        """
        Deletes a secret from the vault.

        :param vault_id: ID of the vault to delete the secret from
        :param path: path of the secret, include the / at the beginning
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{vault_id}/secrets?path={path}')

    def access(self, vault_id: str, path: str, get_metadata: bool = False) -> dict:
        """
        Accesses a secret from the vault.

        :param vault_id: ID of the vault to get the secret from
        :param path: path of the secret, include the / at the beginning
        :param get_metadata: whether or not to get the metadata of the secret
        :return: Details of the secret.
        """

        params = {'getmetadata': get_metadata}
        return self.britive.get(f'{self.base_url}/{vault_id}/secrets?path={path}', params=params)
