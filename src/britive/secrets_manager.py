import json


class SecretsManager:
    def __init__(self, britive):
        self.vaults = Vaults(britive)
        self.password_policies = PasswordPolicies(britive)
        self.secrets = Secrets(britive)
        self.policies = Policies(britive)
        self.static_secret_templates = StaticSecretTemplates(britive)
        self.resources = Resources(britive)
        self.folders = Folders(britive)


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
        users: list = [],
        tags: list = [],
        channels: list = [],
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

        if default_notification_medium_id == '':
            for medium in self.britive.notification_mediums.list():
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

        return self.britive.post(
            f'{self.britive.base_url}/v1/secretmanager/keys/rotate'
        )


class PasswordPolicies:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager/pwdpolicies'

    def get(self, password_policy_id: str) -> dict:
        """
        Provide details of the given password policy, from a password policy id.

        :param password_policy_id: The ID  of the password policy.
        :return: Details of the specified password policy.
        """

        return self.britive.get(f'{self.base_url}/{password_policy_id}')

    def list(self) -> list:
        """
        Provide a list of all password policies

        :return: List of all password policies
        """

        return self.britive.get(self.base_url)

    def create(
        self,
        name: str,
        description: str = 'Default description',
        password_type: str = 'alphanumeric',
        min_password_length: int = 8,
        has_upper_case_chars: bool = True,
        has_lower_case_chars: bool = True,
        has_numbers: bool = True,
        has_special_chars: bool = True,
        allowed_special_chars: str = '@#$%\\(\',)'
    ) -> dict:
        """
        Creates a new password policy.

        :param name: required, name of the password policy
        :param description: description of the password policy
        :param password_type: type of password to use for the policy
        :param min_password_length: minimum length of the password
        :param has_upper_case_chars: whether or not to require uppercase characters
        :param has_lower_case_chars: whether or not to require lowercase characters
        :param has_numbers: whether or not to require numbers
        :param has_special_chars: whether or not to require special characters
        :param allowed_special_chars: a string of special characters to allow in the password
        :return: Details of the newly created password policy.
        """

        params = {
            'name': name,
            'description': description,
            'passwordType': password_type,
            'minPasswordLength': min_password_length,
            'hasUpperCaseChars': has_upper_case_chars,
            'hasLowercaseChars': has_lower_case_chars,
            'hasNumbers': has_numbers,
            'hasSpecialChars': has_special_chars,
            'allowedSpecialChars': allowed_special_chars,
        }
        return self.britive.post(self.base_url, json=params)

    def create_pin(
        self, 
        name: str, 
        description: str = 'Default description', 
        pin_length: int = 4
    ) -> dict:
        """
        Creates a new pin password policy.

        :param name: required, name of the pin password policy
        :param description: description of the pin password policy
        :param pin_length: length of the pin to use for the policy
        :return: Details of the newly created pin password policy.
        """

        params = {
            'name': name,
            'description': description,
            'pinLength': pin_length,
            'passwordType': 'pin',
        }
        return self.britive.post(self.base_url, json=params)

    def update(self, password_policy_id: str, **kwargs) -> None:
        """
        Updates a password policy.

        :param password_policy_id: the ID of the password policy
        :param kwargs: Valid fields are...
            name: name of the password policy
            description: description of the password policy
            passwordType: type of password to use for the policy
            minPasswordLength: minimum length of the password
            hasUpperCaseChars: whether or not to require uppercase characters
            hasLowercaseChars: whether or not to require lowercase characters
            hasNumbers: whether or not to require numbers
            hasSpecialChars: whether or not to require special characters
            allowedSpecialChars: a string of special characters to allow in the password
            pinLength: the length of the pin to use for the policy (only for pins)
        :return: None
        """

        return self.britive.patch(f'{self.base_url}/{password_policy_id}', json=kwargs)

    def delete(self, password_policy_id: str) -> None:
        """
        Deletes a password policy.

        :param password_policy_id: the ID of the password policy
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{password_policy_id}')

    def generate_password(self, password_policy_id: str) -> dict:
        """
        Generates a password for the given password policy.

        :param password_policy_id: the ID of the password policy
        :return: the generated the generated password
        """

        params = {'action': 'generatePasswordOrPin'}
        return self.britive.get(f'{self.base_url}/{password_policy_id}', params=params)[
            'passwordOrPin'
        ]

    def validate(self, password_policy_id: str, password: str) -> dict:
        """
        Validates a password for the given password policy.

        :param password_policy_id: the ID of the password policy
        :param password: the password to validate
        :return: whether or not the password is valid
        """

        params = {'id': password_policy_id, 'passwordOrPin': password}
        return self.britive.post(
            f'{self.base_url}?action=validatePasswordOrPin', json=params
        )


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


class Secrets:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager/vault'

    def create(
        self,
        name: str,
        vault_id: str,
        path: str = '/',
        static_secret_template_id: str = '7a5f41d8-f7af-46a0-88f7-edf0403607ae',
        secret_mode: str = 'shared',
        secret_nature: str = 'static',
        value: dict = {'Note': 'This is the default note'},
        file: bytes = None
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

        if not file:
            return self.britive.post(
                f'{self.base_url}/{vault_id}/secrets?path={path}',
                json={
                    'name': name,
                    'entityType': 'secret',
                    'staticSecretTemplateId': static_secret_template_id,
                    'secretMode': secret_mode,
                    'secretNature': secret_nature,
                    'value': value,
                }
            )
        else:
            secret_data = {
                'entityType': 'secret',
                'name': name,
                'staticSecretTemplateId': static_secret_template_id,
                'secretMode': secret_mode,
                'secretNature': secret_nature,
                'value': value,
            }
            return self.britive.post_upload(
                f'{self.base_url}/{vault_id}/secrets/file?path={path}',
                files={'file': file, 'secretData': (None, json.dumps(secret_data))},
            )

    def update(self, vault_id: str, path: str = '/', value: dict = {}) -> None:
        """
        Updates a secret's value

        :param vault_id: ID of the vault to update the secret in
        :param path: path of the secret, include the / at the beginning
        :param value: value of the secret
        :return: None
        """

        return self.britive.patch(
            f'{self.base_url}/{vault_id}/secrets?path={path}', json={'value': value}
        )

    def get(
        self,
        vault_id: str,
        path: str,
        secret_type: str = 'node',
        filter_type: str = None,
        recursive_secrets: bool = False,
        get_metadata: bool = True
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
        return self.britive.get(
            f'{self.base_url}/{vault_id}/secrets?path={path}', params=params
        )

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
        return self.britive.get(
            f'{self.base_url}/{vault_id}/secrets?path={path}', params=params
        )


class Policies:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/policy-admin/policies'

    def list(self, path: str = '/', filter_str: str = None) -> dict:
        """
        Gets all policies in the vault.

        :param path: path of the policy, include the / at the beginning
        :param filter_str: filter to apply to the listing
        :return: Details of the policies.
        """

        params = {'resource': path, 'consumer': 'secretmanager'}
        if filter:
            params['filter'] = filter_str
        return self.britive.get(f'{self.base_url}', params=params)

    def delete(self, policy_id: str, path: str = '/') -> None:
        """
        Deletes a policy from the vault.

        :param policy_id: ID of the policy to delete
        :param path: path of the policy, include the / at the beginning
        :return: None
        """

        params = {'consumer': 'secretmanager', 'resource': path}
        return self.britive.delete(f'{self.base_url}/{policy_id}', params=params)

    def build(
        self,
        name: str,
        description: str = '',
        draft: bool = False,
        active: bool = True,
        read_only: bool = False,
        users: list = None,
        tags: list = None,
        service_identities: list = None,
        ips: list = None,
        from_time: str = None,
        to_time: str = None,
        approval_notification_medium: str = None,
        time_to_approve: int = 5,
        approver_users: list = None,
        approver_tags: list = None,
        access_type: str = 'Allow',
    ) -> dict:

        """
        Builds a policy to be uploaded to the vault.

        :param name: name of the policy
        :param description: description of the policy
        :param draft: whether or not the policy is a draft
        :param active: whether or not the policy is active
        :param read_only: whether or not the policy is read only
        :param users: list of users to apply the policy to
        :param tags: list of tags to apply the policy to
        :param service_identities: list of service identities to apply the policy to
        :param ips: list of IPs to apply the policy to
        :param from_time: start time of the policy
        :param to_time: end time of the policy
        :param approval_notification_medium: notification medium to use for approval
        :param time_to_approve: time to approve the policy
        :param approver_users: list of users to approve the policy
        :param approver_tags: list of tags to approve the policy
        :param access_type: access type of the policy
        :return: policy to be uploaded to the vault.
        """

        policy = self.britive.policies.build(
            name=name,
            active=active,
            description=description,
            draft=draft,
            access_type=access_type,
            read_only=read_only,
            users=users,
            tags=tags,
            service_identities=service_identities,
            ips=ips,
            from_time=from_time,
            to_time=to_time,
            approval_notification_medium=approval_notification_medium,
            time_to_approve=time_to_approve,
            approver_users=approver_users,
            approver_tags=approver_tags,
        )
        policy.pop('permissions', None)
        policy.pop('roles', None)
        policy['accessLevel'] = 'SM_Manage'
        return policy

    def create(self, policy: dict, path: str = '/') -> dict:
        """
        Creates  a policy in the vault.

        :param policy: policy to create
        :param path: path of the policy, include the / at the beginning
        :return: Details of the policy.
        """

        return self.britive.post(f'{self.base_url}?resource={path}&consumer=secretmanager', json=policy)


class StaticSecretTemplates:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = (
            f'{self.britive.base_url}/v1/secretmanager/secret-templates/static'
        )

    def get(self, secret_template_id: str) -> dict:
        """
        Gets a secret template from the vault.

        :param secret_template_id: ID of the secret template to get
        :return: Details of the secret template.
        """

        return self.britive.get(f'{self.base_url}/{secret_template_id}')

    def list(self, filter_str: str = None) -> dict:
        """
        Lists all secret templates in the vault.

        :param filter_str: filter to apply to the listing
        :return: Details of the secret templates.
        """

        params = {'filter': filter_str}
        return self.britive.get(f'{self.base_url}', params=params)

    def delete(self, secret_template_id: str) -> None:
        """
        Deletes a secret template from the vault.

        :param secret_template_id: ID of the secret template to delete
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{secret_template_id}')

    def create(
        self,
        name: str,
        password_policy_id: str,
        description: str = '',
        rotation_interval: int = 30,
        parameters: list = None
    ) -> dict:
        """
        Creates a secret template

        :param name: name of the secret template
        :param password_policy_id: ID of the password policy to use
        :param description: description of the secret template
        :param rotation_interval: rotation interval of the secret template
        :param parameters: list of parameters to use in the secret template
        :return: Details of the secret template.
        """

        params = {
            'secretType': name,
            'passwordPolicyId': password_policy_id,
            'description': description,
            'rotationInterval': rotation_interval,
            'parameters': [parameters],
        }

        return self.britive.post(f'{self.base_url}', json=params)

    def update(self, static_secret_template_id: str, **kwargs) -> None:
        """
        Updates a secret template

        :param static_secret_template_id: ID of the secret template to update
        :param kwargs: key-value pairs to update the secret template with
                valid keys are:
                    name: name of the secret template
                    passwordPolicyId: ID of the password policy to use
                    description: description of the secret template
                    rotationInterval: rotation interval of the secret template
                    parameters: list of parameters to use in the secret template
        :return: None
        """

        return self.britive.patch(
            f'{self.base_url}/{static_secret_template_id}', json=kwargs
        )


class Resources:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager/resourceContainers'

    def get(self, path: str = '/') -> dict:
        """
        Gets a resource from the vault

        :param path: path of the resource, include the / at the beginning
        :return: Details of the resource.
        """

        params = {'path': path}
        return self.britive.get(f'{self.base_url}', params=params)
