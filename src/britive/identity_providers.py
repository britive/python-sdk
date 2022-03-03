class IdentityProviders:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/identity-providers'
        self.scim_tokens = ScimTokens(britive)
        self.scim_attributes = ScimAttributes(britive)

    def list(self) -> list:
        """
        Return list of identity providers.

        :return: List of identity providers
        """

        return self.britive.get(self.base_url)

    def get(self, identity_provider_id: str) -> dict:
        """
        Return details of the specified identity provider.

        :param identity_provider_id: The ID of the identity provider.
        :return: Details of the identity provider.
        """

        return self.britive.get(f'{self.base_url}/{identity_provider_id}')

    def get_by_id(self, identity_provider_id: str) -> dict:
        """
        Return details of the given identity provider.

        Equivalent to `get()`. Exists for parity with `get_by_name` since identity providers can be found by
        `name` in addition to `id`.
        :param identity_provider_id:
        :return: Details of the identity provider.
        """

        return self.get(identity_provider_id=identity_provider_id)

    def get_by_name(self, identity_provider_name: str) -> dict:
        """
        Return details of the given identity provider.

        :param identity_provider_name: Name of the identity provider.
        :return: Details of the identity provider.
        """

        params = {
            'name': identity_provider_name
        }
        return self.britive.get(self.base_url, params=params)

    def signing_certificate(self) -> str:
        """
        Return the signing certificate for the Britive tenant.

        This certificate would be used to configure a new SSO identity provider. The certificate is the same
        across all identity providers in the Britive tenant.

        It is left to the caller to persist the certificate to disk, if required. File extension is `.cer`.

        :return: The signing certificate.
        """

        return self.britive.get(f'{self.base_url}/signing-certificate')

    def create(self, name: str, description: str = None) -> dict:
        data = {
            'name': name,
            'description': description or ''
        }
        return self.britive.post(self.base_url, json=data)

    def update(self, identity_provider_id: str, name: str = None, description: str = None, sso_provider: str = None,
               scim_provider: str = None) -> None:
        """
        Updates an identity provider.

        If `Azure` is used for SSO and SCIM provisioning, both SSO and SCIM providers need to be set to `Azure`.

        :param identity_provider_id: The ID of the identity provider.
        :param name: The name of the identity provider. If omitted will default to existing name.
        :param description: The description of the identity provider. If omitted will default to existing description.
        :param sso_provider: The SSO provider. Valid values are...

            - Generic
            - Azure

            If omitted will default to existing SSO provider.
        :param scim_provider: The SCIM provider. Valid values are...

            - Generic
            - Azure

            If omitted will default to existing SCIM provider.
        :return: None
        """

        # collect what needs to be updated
        possible_updates = {
            'name': name,
            'description': description,
            'scimProvider': scim_provider,
            'ssoProvider': sso_provider
        }
        updates = {k: v for k, v in possible_updates.items() if v is not None}

        # collect what already exists
        idp = self.get(identity_provider_id=identity_provider_id)
        existing = {
            'name': idp['name'],
            'description': idp['description'],
            'scimProvider': idp['scimProvider'],
            'ssoProvider': idp['ssoProvider']
        }

        # merge in any updates
        data = {**existing, **updates}

        # and finally perform the update
        return self.britive.patch(f'{self.base_url}/{identity_provider_id}', json=data)

    def delete(self, identity_provider_id: str) -> None:
        """
        Delete an identity provider.

        Performing this action WILL result in any remaining users associated with the identity provider losing access
        to the tenant.

        :param identity_provider_id: The ID of the identity provider.
        :return: None
        """

        self.britive.delete(f'{self.base_url}/{identity_provider_id}')

    def configure_mfa(self, identity_provider_id: str, root_user: bool = None, non_root_user: bool = None) -> None:
        """
        Enable or disable both root user multi factor authentication (MFA) and/or non root user MFA.

        :param identity_provider_id: The ID of the identity provider.
        :param root_user: Whether to enable or disable root user MFA. If omitted will default to existing configuration.
        :param non_root_user: Whether to enable or disable non root user MFA. If omitted will default to existing
            configuration.
        :return: None
        """

        # collect what needs to be updated
        possible_updates = {
            'mfaEnabled': non_root_user,
            'mfaEnabledRootUser': root_user
        }
        updates = {k: v for k, v in possible_updates.items() if v is not None}

        # collect what already exists
        idp = self.get(identity_provider_id=identity_provider_id)
        existing = {
            'mfaEnabled': idp['mfaEnabled'],
            'mfaEnabledRootUser': idp['mfaRootUserEnabled']
        }

        # merge in any updates
        data = {**existing, **updates}

        return self.britive.patch(f'{self.base_url}/{identity_provider_id}/mfa', json=data)

    def set_metadata(self, identity_provider_id: str, metadata_xml: str) -> dict:
        """
        Set SAML metadata for the specified identity provider.

        This metadata is in XML format, provided a a string, and would be obtained from the identity provider.

        :param identity_provider_id: The ID of the identity provider.
        :param metadata_xml: An XML string (str) representing SAML metadata obtained from the identity provider.
        :return: Details of the SAML metadata that was uploaded.
        """
        return self.britive.patch_upload(
            url=f'{self.base_url}/{identity_provider_id}/saml-metadata',
            file_content_as_str=metadata_xml,
            filename='file',
            content_type='text/xml'
        )


class ScimTokens:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/identity-providers'

    def create(self, identity_provider_id: str, token_expiration_days: int = 90) -> dict:
        """
        Create a SCIM token associated with the specified identity provider.

        Once created, any old token associated with the identity provider will be removed. Any identity provider can
        have only one SCIM token at any given time.

        The token that is generated will only be returned in a response once. It is the responsibility of the caller
        to persist this token.

        :param identity_provider_id: The ID of the identity provider.
        :param token_expiration_days: The number of days in which token would expire since it was last used.
            Value values are between 1 and 90.
        :return: Details of the newly created SCIM token.
        """

        data = {
            'tokenExpirationDays': token_expiration_days
        }
        return self.britive.post(f'{self.base_url}/{identity_provider_id}/scim-token', json=data)

    def get(self, identity_provider_id: str) -> dict:
        """
        Return details of SCIM token associated with the specified identity provider.

        :param identity_provider_id: The ID of the identity provider.
        :return: Details of the SCIM token.
        """

        return self.britive.get(f'{self.base_url}/{identity_provider_id}/scim-token')

    def update(self, identity_provider_id: str, token_expiration_days: int) -> None:
        """
        Update the token expiration days for the specified identity provider.

        :param identity_provider_id: The ID of the identity provider.
        :param token_expiration_days: The number of days in which token would expire since it was last used.
            Value values are between 1 and 90.
        :return: None
        """

        data = {
            'tokenExpirationDays': token_expiration_days
        }
        return self.britive.patch(f'{self.base_url}/{identity_provider_id}/scim-token', json=data)


class ScimAttributes:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/identity-providers'

    def list(self) -> list:
        """
        Return a list of SCIM attributes used for provisioning from the target system.

        :return: List of SCIM attributes.
        """

        return self.britive.get(f'{self.base_url}/scim-attributes')

    def update_mapping(self, identity_provider_id: str, mappings: list) -> None:
        """
        Add/remove SCIM mappings for the specified identity provider.

        When new SCIM mappings are added, the existing SCIM mappings for the identity attribute are deleted, if they
        are already defined.
        :param identity_provider_id: The ID of the identity provider.
        :param mappings: A list of identity attributes to add/remove. Each element in the list is a dict of the
            following format.

                {
                    "scimAttributeName": "addresses[type eq \"home\"].country",
                    "builtIn": False|True,
                    "attributeId": "HSvfZ1b74HUd7o8ai5Wo",
                    "attributeName": "country",
                    "op": "add"|"remove"
                }

            Each key is explained below in further detail.

            - scimAttributeName: The name of the SCIM attribute returned by
                `britive.identity_providers.scim_attributes.list()`.
            - builtIn: True if the identity attribute is from the built-in list, False if user generated.
            - attributeId: The ID of the identity attribute to be mapped with the identity provider. This can be
                obtained by calling `britive.identity_attributes.list()`.
            - attributeName: The name of the identity attribute to be mapped with the identity provider. This can be
                obtained by calling `britive.identity_attributes.list()`.
            - op: The operation to perform. Valid values are `add` and `remove`.
        :return: None
        """

        return self.britive.patch(f'{self.base_url}/{identity_provider_id}/scim-attribute-mappings', json=mappings)
