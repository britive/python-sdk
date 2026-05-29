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

    def metadata(self, vault_id: str, path: str) -> dict:
        """
        Retrieve metadata for a secret, including rotation configuration.

        :param vault_id: ID of the vault.
        :param path: path of the secret, include the / at the beginning.
        :return: Secret metadata including rotation interval, last/next rotation timestamps.
        """

        return self.britive.get(f'{self.base_url}/{vault_id}/secret-metadata?path={path}')

    def rotation_details(self, vault_id: str, path: str) -> dict:
        """
        Retrieve admin-level secret details including rotation targets and configuration.

        :param vault_id: ID of the vault.
        :param path: path of the secret, include the / at the beginning.
        :return: Secret rotation details including resource, account, and rotation template mappings.
        """

        return self.britive.get(f'{self.base_url}/{vault_id}/admin/accesssecrets?path={path}')

    def update_rotation(self, vault_id: str, path: str, rotation_config: dict = None, **kwargs) -> None:
        """
        Update rotation configuration for a secret.

        The rotation config is sent as part of the secret PATCH body. This can include
        resource/account mapping, rotation template, notification settings, etc.

        :param vault_id: ID of the vault.
        :param path: path of the secret, include the / at the beginning.
        :param rotation_config: dict of rotation configuration fields to set on the secret.
        :param kwargs: additional fields to include in the PATCH body.
        :return: None
        """

        params = {}
        if rotation_config:
            params.update(rotation_config)
        params.update(kwargs)
        return self.britive.patch(f'{self.base_url}/{vault_id}/secrets?path={path}', json=params)

    def rotate(self, vault_id: str, path: str, value: dict = None, sync_to_target: bool = True) -> dict:
        """
        Trigger rotation for a secret (update password and sync to target).

        Updates the secret value and optionally syncs the new value to the mapped target resource.
        Requires that the secret has a resource and account mapped in its rotation details.

        :param vault_id: ID of the vault.
        :param path: path of the secret, include the / at the beginning.
        :param value: new secret value dict (e.g. {'Password': 'newpass'}). If None, only sync is triggered.
        :param sync_to_target: whether to sync the updated value to the target resource. Defaults to True.
        :return: Details of the rotation operation.
        """

        params = {'syncToTarget': sync_to_target}
        if value:
            params['value'] = value
        return self.britive.patch(f'{self.base_url}/{vault_id}/secrets?path={path}', json=params)

    def rotation_history(self, vault_id: str, secret_id: str) -> list:
        """
        Retrieve rotation history for a secret.

        :param vault_id: ID of the vault.
        :param secret_id: ID of the secret.
        :return: List of rotation history entries with date, status, executed by, and type.
        """

        return self.britive.get(f'{self.base_url}/{vault_id}/secrets/{secret_id}/rotate/history')

    def versions(self, vault_id: str, secret_id: str) -> list:
        """
        List all versions of a secret.

        :param vault_id: ID of the vault.
        :param secret_id: ID of the secret.
        :return: List of secret versions with version number, creation date, and created by.
        """

        return self.britive.get(f'{self.base_url}/{vault_id}/secrets/{secret_id}/versions')
