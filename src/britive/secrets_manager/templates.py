class StaticSecretTemplates:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager/secret-templates/static'

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
        parameters: list = None,
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

        current = self.get(secret_template_id=static_secret_template_id)

        return self.britive.patch(f'{self.base_url}/{static_secret_template_id}', json={**current, **kwargs})
