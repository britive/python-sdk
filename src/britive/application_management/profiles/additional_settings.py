class AdditionalSettings:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/paps'

    def _build_settings_data(self, **kwargs) -> dict:
        key_mapping = {
            'cred': 'useApplicationCredentialType',
            'con': 'consoleAccess',
            'prog': 'programmaticAccess',
            'proj': 'projectIdForServiceAccount',
        }
        return {key_mapping[k]: v for k, v in kwargs.items() if v is not None}

    def create(
        self,
        profile_id: str,
        use_app_credential_type: bool = None,
        console: bool = None,
        programmatic: bool = None,
        project_id: str = None,
    ) -> None:
        """
        Create or overwrite profile additional settings for GCP, GCP Standalone, and Azure applications.

        :param profile_id: The ID of the profile.
        :param use_app_credential_type: Whether to inherit the credential type from the application.
        :param console: Whether to enable console access for the profile.
        :param programmatic: Whether to enable programmatic access for the profile.
        :param project_id: The project ID for creating service accounts (GCP/GCP Standalone only).
        :return: None.
        """
        data = self._build_settings_data(cred=use_app_credential_type, con=console, prog=programmatic, proj=project_id)
        return self.britive.post(f'{self.base_url}/{profile_id}/additional-settings', json=data)

    def update(
        self,
        profile_id: str,
        use_app_credential_type: bool = None,
        console: bool = None,
        programmatic: bool = None,
        project_id: str = None,
    ) -> None:
        """
        Update specific additional settings for a profile in GCP, GCP Standalone, and Azure applications.

        :param profile_id: The ID of the profile.
        :param use_app_credential_type: Whether to inherit the credential type from the application.
        :param console: Whether to enable console access for the profile.
        :param programmatic: Whether to enable programmatic access for the profile.
        :param project_id: The project ID for creating service accounts (GCP/GCP Standalone only).
        :return: None.
        """
        data = self._build_settings_data(cred=use_app_credential_type, con=console, prog=programmatic, proj=project_id)
        return self.britive.patch(f'{self.base_url}/{profile_id}/additional-settings', json=data)

    def get(self, profile_id: str) -> dict:
        """
        Retrieve additional settings for a profile in GCP, GCP Standalone, and Azure applications.

        :param profile_id: The ID of the profile.
        :return: Details of added attribute.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}/additional-settings')
