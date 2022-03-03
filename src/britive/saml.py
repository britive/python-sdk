
class Saml:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/saml'

    def settings(self, as_list: bool = False) -> any:
        """
        Retrieve the SAML settings for the tenant.

        For historical reasons there was a time in which multiple SAML settings could exist for a given tenant. This
        was to support certificate rotation. However a change in certificate issuance occurred and as a result this
        API call will only ever return 1 item in the list now. As such, `as_list` will default to `False` but returning
        the data as a list will continue to be supported for backwards compatibility.

        :param as_list: There is only 1 set of SAML settings per tenant. The API returns the settings
            as list but since there is only one this python library will return the single settings dict unless this
            parameter is set to True.
        :return: Details of the SAML settings for the tenant.
        """

        settings = self.britive.get(f'{self.base_url}/settings')
        if as_list:
            return settings
        return settings[0]

    def metadata(self) -> str:
        """
        Return the SAML metadata required in the SAML SSO configuration with a service provider.

        This operation is supported only in AWS and Oracle.

        The caller is responsible for saving this content to disk, if needed.

        :return: String representing the SAML XML metadata.
        """

        saml_id = self.settings(as_list=False)['id']

        return self.britive.get(f'{self.base_url}/metadata/{saml_id}')

    def certificate(self):
        """
        Return the SAML certificate required in the SAML SSO configuration with a service provider.

        This operation is applicable for applications that do not support importing SAML metadata.

        The caller is responsible for saving this content to disk, if needed.

        :return: String representing the SAML XML metadata.
        """

        saml_id = self.settings(as_list=False)['id']

        return self.britive.get(f'{self.base_url}/certificate/{saml_id}')
