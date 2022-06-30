class SecretsManager:
    def __init__(self, britive):
        self.vaults = Vaults(britive)
        self.password_policies = PasswordPolicies(britive)


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

class PasswordPolicies():
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager/pwdpolicies'
    def get(self, password_policy_id : str):
        """
        Provide details of the given password policy, from a password policy id.
        :param password_policy_id: The ID  of the password policy.
        :return: Details of the specified password policy.
        
        """
        return self.britive.get(f'{self.base_url}/{password_policy_id}')
        return self.britive.get(self.base_url, params=params)
    def list(self):
        """
        Provide a list of all password policies

        :return: List of all password policies
        """
        return self.britive.get(self.base_url)
    def create(self, name : str, description : str = "Default description", passwordType : str = "alphanumeric", minPasswordLength : int = 8, hasUpperCaseChars : bool = True, hasLowercaseChars : bool = True, hasNumbers : bool = True, hasSpecialChars : bool = True, allowedSpecialChars : str = "@#$%\("):
        """
        Creates a new password policy.

        :param: name - required, name of the password policy
        :param: description, description of the password policy
        :param: passwordType, type of password to use for the policy
        :param: minPasswordLength, minimum length of the password
        :param: hasUpperCaseChars, whether or not to require uppercase characters
        :param: hasLowercaseChars, whether or not to require lowercase characters
        :param: hasNumbers, whether or not to require numbers
        :param: hasSpecialChars, whether or not to require special characters
        :param: allowedSpecialChars, a string of special characters to allow in the password
        :param: pinLength, the length of the pin to use for the policy (only for pins)

        :returns: Details of the newly created password policy.
        
        """
        params = {'name' : name, 'description' : description, 'passwordType' : passwordType, 'minPasswordLength' : minPasswordLength, 'hasUpperCaseChars' : hasUpperCaseChars, 'hasLowercaseChars' : hasLowercaseChars, 'hasNumbers' : hasNumbers, 'hasSpecialChars' : hasSpecialChars, 'allowedSpecialChars' : allowedSpecialChars}
        return self.britive.post(self.base_url, json=params)
    
    def create_pin(self, name : str, description : str = "Default description", pinLength : int = 4):
        """
        Creates a new pin password policy.

        :param: name - required, name of the pin password policy
        :param: description, description of the pin password policy
        :param: pinLength, length of the pin to use for the policy

        :returns: Details of the newly created pin password policy.
        
        """
        params = {'name' : name, 'description' : description, 'pinLength' : pinLength, 'passwordType' : 'pin'}
        return self.britive.post(self.base_url, json=params)
        
    def update(self,password_policy_id : str, **kwargs):
        """
        Updates a passsworld policy

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
        
        :return: none
        """
        creation_defaults = self.get(password_policy_id)
        data = {**creation_defaults, **kwargs}
        return self.britive.patch(f'{self.base_url}/{password_policy_id}', json=data)
    
    def delete(self, password_policy_id: str):
        """
        Deletes a password policy.

        :param password_policy_id: the ID of the password policy

        :return: none
        """
        return self.britive.delete(f'{self.base_url}/{password_policy_id}')
    
    def generate_password(self, password_policy_id: str):
        """
        Generates a password for the given password policy.

        :param password_policy_id: the ID of the password policy

        :return: the generated the generated password
        """
        params = {
            'action': 'generatePasswordOrPin'
        }
        return self.britive.get(f'{self.base_url}/{password_policy_id}', params=params)['passwordOrPin']

    def validate(self, password_policy_id: str, password: str):
        """
        Validates a password for the given password policy.

        :param password_policy_id: the ID of the password policy
        :param password: the password to validate

        :return: whether or not the password is valid
        """
        params = {
            'id' : password_policy_id,
            'passwordOrPin': password
        }
        return self.britive.post(f'{self.base_url}?action=validatePasswordOrPin', json=params)
    
    
