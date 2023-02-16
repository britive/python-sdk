
class Workload:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/workload'
        self.identity_providers = self.IdentityProviders(self)
        self.users = self.User(self)

    class IdentityProviders:
        def __init__(self, workload):
            self.britive = workload.britive
            self.base_url = f'{workload.base_url}/identity-providers'

        def list(self, idp_type: str = None) -> list:
            """
            Return a list of all workload identity providers.

            :param idp_type: Optional filter to apply to reduce the results to a specific workload identity provider
                type. Valid values are `AWS` and `OIDC`.
            :returns: List of all workload identity providers.
            """

            params = {}
            if idp_type:
                params['type'] = idp_type
            return self.britive.get(self.base_url, params=params)

        def get(self, workload_identity_provider_id: int) -> dict:
            """
            Return details of the specified workload identity provider.

            :param workload_identity_provider_id: The ID of the workload identity provider.
            :returns: Details of the specified workload identity provider.
            """

            return self.britive.get(f'{self.base_url}/{workload_identity_provider_id}')

        def create(self, **kwargs) -> dict:
            """
            Create a workload identity provider.

            This method accepts a list of kwargs which match the required and optional fields for creating a
            workload identity provider. It mostly exists to support the creation of new workload identity provider
            types before this SDK can be updated to support the new type natively.

            Generally, the caller should opt to use the `create_aws` or `create_oidc` methods instead of calling
            this method directly.

            :param kwargs: A list of keyword arguments which will be provided directly to the API backend without
                any further inspection. Valid fields are `name`, `description`, `idpType`, `attributesMap`, and
                `validationWindow`. For the AWS provider an additional field `maxDuration` is valid. For the OIDC
                provider additional fields `issuerUrl` and `allowedAudiences` are valid.
            :returns: Details of the newly created workload identity provider.
            """

            return self.britive.post(self.base_url, json=kwargs)

        def create_aws(self, name: str, attributes_map: dict = None, description: str = None,
                       validation_window: int = 30, max_duration: int = 5) -> dict:
            """
            Create an AWS workload identity provider.

            :param name: Name of the AWS workload identity provider.
            :param attributes_map: The mapping of the available AWS workload token fields to custom identity attributes
                which are associated with service identities. Defaults to None.
            :param description: Optional description of the AWS workload identity provider.
            :param validation_window: The number of seconds allowed to validate the AWS workload token from its
                "issued time". Defaults to 30 seconds.
            :param max_duration: The max number of hours (whole numbers only) for which the AWS workload token is valid.
            :returns: Details of the newly created AWS workload identity provider.
            """

            params = {
                'name': name,
                'idpType': 'AWS',
                'validationWindow': validation_window,
                'maxDuration': max_duration
            }
            if description:
                params['description'] = description
            if attributes_map:
                params['attributesMap'] = attributes_map

            return self.create(**params)

        def create_oidc(self, name: str, issuer_url: str, attributes_map: dict = None, description: str = None,
                        validation_window: int = 30, allowed_audiences: list = None) -> dict:
            """
            Create an AWS workload identity provider.

            :param name: Name of the OIDC workload identity provider.
            :param issuer_url: The issuer url for the OIDC provider.
            :param attributes_map: The mapping of the available OIDC workload token fields to custom identity attributes
                which are associated with service identities. Defaults to None.
            :param description: Optional description of the AWS workload identity provider.
            :param validation_window: The number of seconds allowed to validate the AWS workload token from its
                "issued time". Defaults to 30 seconds.
            :param allowed_audiences: The list of allowed audience values as strings. Defaults to None.
            :returns: Details of the newly created OIDC workload identity provider.
            """

            params = {
                'name': name,
                'idpType': 'OIDC',
                'validationWindow': validation_window,
                'issuerUrl': issuer_url
            }
            if description:
                params['description'] = description
            if allowed_audiences:
                params['allowedAudiences'] = attributes_map

            return self.create(**params)

        def update(self, workload_identity_provider_id: int, **kwargs) -> dict:
            """
            Updates details of the specified workload identity provider.

            :param workload_identity_provider_id: The ID of the workload identity provider.
            :param kwargs: Any attributes of the workload identity provider that should be updated. Reference the
                `create` method for details on what attributes are available.
            :returns: Details of the updated workload identity provider.
            """
            kwargs['id'] = workload_identity_provider_id
            return self.britive.put(self.base_url, json=kwargs)

        def delete(self, workload_identity_provider_id) -> None:
            """
            Deletes a workload identity provider.

            :param workload_identity_provider_id: The ID of the workload identity provider.
            :returns: None.
            """
            self.britive.delete(f'{self.base_url}/{workload_identity_provider_id}')
            return None

        def generate_attribute_map(self, idp_attribute_name: str, custom_identity_attribute_name: str = None,
                                   custom_identity_attribute_id: str = None) -> dict:
            """
            Generates a dictionary that can be appended to a list used for the attributes_map.

            :param idp_attribute_name: The name of the workload identity provider attribute to map. This will always
                be a string as it is controlled by the identity provider.
            :param custom_identity_attribute_name: The name of the Britive custom identity attribute. One of
                `custom_identity_attribute_name` or `custom_identity_attribute_id` must be provided. The name will be
                translated to the ID of the custom identity attribute on behalf of the caller.
            :param custom_identity_attribute_id: The id of the Britive custom identity attribute. One of
                `custom_identity_attribute_name` or `custom_identity_attribute_id` must be provided.
            :returns: Dictionary representing the attribute map.
            """

            if custom_identity_attribute_id and custom_identity_attribute_name:
                raise ValueError('only one of custom_identity_attribute_id and custom_identity_attribute_name '
                                 'should be provided')

            if not custom_identity_attribute_id and not custom_identity_attribute_name:
                raise ValueError('one of custom_identity_attribute_id or custom_identity_attribute_name '
                                 'should be provided')

            if custom_identity_attribute_name:
                found = False
                for attr in self.britive.identity_attributes.list():
                    if attr['name'] == custom_identity_attribute_name:
                        custom_identity_attribute_id = attr['id']
                        found = True
                        break
                if not found:
                    raise ValueError(f'custom_identity_attribute_name value of {custom_identity_attribute_name} '
                                     f'not found.')

            return {
                'idpAttr': idp_attribute_name,
                'userAttr': custom_identity_attribute_id
            }

    class Users:
        def __init__(self, workload):
            self.britive = workload.britive
            self.base_url: str = workload.base_url + '/users/{id}/identity-provider'  # will .format(id=...) later

        def get(self, service_identity_id: str) -> dict:
            """
            Returns details about the workload identity provider associated with the specified service identity.

            :param service_identity_id: The ID of the service identity
            :returns: Details about the workload identity provider associated with the specified service identity.
            """

            return self.britive.get(self.base_url.format(id=service_identity_id))

        def associate