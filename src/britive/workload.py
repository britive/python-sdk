from . import exceptions
from typing import Union


class Workload:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/workload'
        self.identity_providers = self.IdentityProviders(self)
        self.service_identities = self.ServiceIdentities(self)
        self.scim_user = self.ScimUser(self)

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

        def _build_attributes_map_list(self, attributes_map: dict):
            # first get list of existing custom identity attributes and build some helpers
            existing_attrs = [attr for attr in self.britive.identity_attributes.list() if not attr['builtIn']]
            existing_attr_ids = [attr['id'] for attr in existing_attrs]
            attrs_by_name = {attr['name']: attr['id'] for attr in existing_attrs}

            # for each attributeMap key/value provided ensure we convert to ID and build the list
            attrs_list = []
            for idp_attr, custom_identity_attribute in attributes_map.items():
                if custom_identity_attribute not in existing_attr_ids:
                    custom_identity_attribute = attrs_by_name.get(custom_identity_attribute, None)
                if not custom_identity_attribute:
                    raise ValueError(f'custom identity attribute name {custom_identity_attribute} not found.')
                attrs_list.append(
                    {
                        'idpAttr': idp_attr,
                        'userAttr': custom_identity_attribute
                    }
                )
            return attrs_list

        def create(self, **kwargs) -> dict:
            """
            Create a workload identity provider.

            This method accepts a list of kwargs which match the required and optional fields for creating a
            workload identity provider. It mostly exists to support the creation of new workload identity provider
            types before this SDK can be updated to support the new type natively.

            Generally, the caller should opt to use the `create_aws` or `create_oidc` methods instead of calling
            this method directly.

            The field `attributesMap` is in format `{'idp_attr_value': 'custom_identity_attribute_name_or_id', ...}`.

            :param kwargs: A list of keyword arguments which will be provided directly to the API backend without
                any further inspection. Valid fields are `name`, `description`, `idpType`, `attributesMap`, and
                `validationWindow`. For the AWS provider an additional field `maxDuration` is valid. For the OIDC
                provider additional fields `issuerUrl` and `allowedAudiences` are valid.
            :returns: Details of the newly created workload identity provider.
            """

            if 'attributesMap' in kwargs.keys():
                kwargs['attributesMap'] = self._build_attributes_map_list(attributes_map=kwargs['attributesMap'])

            return self.britive.post(self.base_url, json=kwargs)

        def create_aws(self, name: str, attributes_map: dict, description: str = None,
                       validation_window: int = 30, max_duration: int = 5) -> dict:
            """
            Create an AWS workload identity provider.

            :param name: Name of the AWS workload identity provider.
            :param attributes_map: The mapping of the available AWS workload token fields to custom identity attributes
                which are associated with service identities. Defaults to None.Can provide either the name of the
                custom identity attribute or the ID.
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
            Create an OIDC workload identity provider.

            :param name: Name of the OIDC workload identity provider.
            :param issuer_url: The issuer url for the OIDC provider.
            :param attributes_map: The mapping of the available OIDC workload token fields to custom identity attributes
                which are associated with service identities. Defaults to None. Can provide either the name of the
                custom identity attribute or the ID.
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
                params['allowedAudiences'] = allowed_audiences
            if attributes_map:
                params['attributesMap'] = attributes_map

            return self.create(**params)

        def update(self, workload_identity_provider_id: int, **kwargs) -> dict:
            """
            Updates a workload identity provider.

            This method accepts a list of kwargs which match the required and optional fields for creating a
            workload identity provider. It mostly exists to support the update of new workload identity provider
            types before this SDK can be updated to support the new type natively.

            Generally, the caller should opt to use the `update_aws` or `update_oidc` methods instead of calling
            this method directly.

            The field `attributesMap` is in format `{'idp_attr_value': 'custom_identity_attribute_name_or_id', ...}`.

            :param workload_identity_provider_id: The ID of the workload identity provider to update.
            :param kwargs: A list of keyword arguments which will be provided directly to the API backend without
                any further inspection. Valid fields are `name`, `description`, `idpType`, `attributesMap`, and
                `validationWindow`. For the AWS provider an additional field `maxDuration` is valid. For the OIDC
                provider additional fields `issuerUrl` and `allowedAudiences` are valid.
            :returns: Details of the updated workload identity provider.
            """

            kwargs['id'] = workload_identity_provider_id

            if 'attributesMap' in kwargs.keys():
                kwargs['attributesMap'] = self._build_attributes_map_list(attributes_map=kwargs['attributesMap'])

            # since this is a PUT call and not a PATCH call we need to get the existing idp configuration
            # and merge in the things that have changed

            existing = self.get(workload_identity_provider_id=workload_identity_provider_id)
            return self.britive.put(self.base_url, json={**existing, **kwargs})

        def update_aws(self, workload_identity_provider_id: int, name: str = None, attributes_map: dict = None,
                       description: str = None, validation_window: int = None, max_duration: int = None) -> dict:
            """
            Update an AWS workload identity provider.

            All fields except `workload_identity_provider_id` are optional.

            :param workload_identity_provider_id: The ID of the workload identity provider to update.
            :param name: Name of the AWS workload identity provider.
            :param attributes_map: The mapping of the available AWS workload token fields to custom identity attributes
                which are associated with service identities.Can provide either the name of the custom identity
                attribute or the ID.
            :param description: Description of the AWS workload identity provider.
            :param validation_window: The number of seconds allowed to validate the AWS workload token from its
                "issued time".
            :param max_duration: The max number of hours (whole numbers only) for which the AWS workload token is valid.
            :returns: Details of the updated AWS workload identity provider.
            """

            params = {
                'idpType': 'AWS'
            }

            if name:
                params['name'] = name
            if description:
                params['description'] = description
            if validation_window:
                params['validationWindow'] = validation_window
            if max_duration:
                params['maxDuration'] = max_duration
            if attributes_map:
                params['attributesMap'] = attributes_map

            return self.update(workload_identity_provider_id=workload_identity_provider_id, **params)

        def update_oidc(self, workload_identity_provider_id: int, name: str = None, issuer_url: str = None,
                        attributes_map: dict = None, description: str = None, validation_window: int = None,
                        allowed_audiences: list = None) -> dict:
            """
            Update an OIDC workload identity provider.

            All fields except `workload_identity_provider_id` are optional.

            :param workload_identity_provider_id: The ID of the workload identity provider to update.
            :param name: Name of the OIDC workload identity provider.
            :param issuer_url: The issuer url for the OIDC provider.
            :param attributes_map: The mapping of the available OIDC workload token fields to custom identity attributes
                which are associated with service identities. Can provide either the name of the custom identity
                attribute or the ID.
            :param description: Description of the AWS workload identity provider.
            :param validation_window: The number of seconds allowed to validate the AWS workload token from its
                "issued time".
            :param allowed_audiences: The list of allowed audience values as strings.
            :returns: Details of the update OIDC workload identity provider.
            """

            params = {
                'idpType': 'OIDC'
            }

            if name:
                params['name'] = name
            if description:
                params['description'] = description
            if validation_window:
                params['validationWindow'] = validation_window
            if issuer_url:
                params['issuerUrl'] = issuer_url
            if attributes_map:
                params['attributesMap'] = attributes_map
            if allowed_audiences:
                params['allowedAudiences'] = allowed_audiences

            return self.update(workload_identity_provider_id=workload_identity_provider_id, **params)

        def delete(self, workload_identity_provider_id) -> None:
            """
            Deletes a workload identity provider.

            :param workload_identity_provider_id: The ID of the workload identity provider.
            :returns: None.
            """
            return self.britive.delete(f'{self.base_url}/{workload_identity_provider_id}')

        def generate_attribute_map(self, idp_attribute_name: str, custom_identity_attribute_name: str = None,
                                   custom_identity_attribute_id: str = None) -> dict:
            """
            Generates a dictionary that can be appended to a list used for the `attributesMap`.

            This method would mostly be used when invoking the `create` or `update` methods directly instead of
            using the type specific (`create_aws`, `create_oidc`, `update_aws`, `update_oidc`) methods which provide
            a more pythonic way to capture the attribute mappings.

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

    class ServiceIdentities:
        def __init__(self, workload):
            self.britive = workload.britive
            self.base_url: str = workload.base_url + '/users/{id}/identity-provider'  # will .format(id=...) later

        def get(self, service_identity_id: str) -> Union[dict, None]:
            """
            Returns details about the workload identity provider associated with the specified service identity.

            :param service_identity_id: The ID of the service identity.
            :returns: Details about the workload identity provider associated with the specified service identity.
                Returns None if there is no workload identity provider associated with the specified service identity.
            """

            return self.britive.get(self.base_url.format(id=service_identity_id))

        def assign(self, service_identity_id: str, idp_id: str, federated_attributes: dict,
                   token_duration: int = 300) -> dict:
            """
            Associates an OIDC provider with the specified Service Identity.

            :param service_identity_id: The ID of the service identity.
            :param idp_id: The ID of the OIDC Identity Provider.
            :param token_duration: Duration in seconds (from now) before a token provided by the client expires.
                This will be evaluated alongside the OIDC JWT expiration field and the earlier of the two values
                will govern when the token expires. This field is optional and defaults to 300 seconds.
            :param federated_attributes: An attribute map where keys are the custom attribute ids or names
                and values are strings or list of strings (for multivalued attributes) which map back to the mapped
                token claims.
            :returns: Details of the newly assigned workload identity provider.
            """

            mapping_attributes = []
            converted_federated_attributes = {}
            converted_attributes = self.britive.service_identities.custom_attributes._build_list(
                operation='add',
                custom_attributes=federated_attributes
            )

            for attr in converted_attributes:
                custom_attr = attr['customUserAttribute']
                attr_id = custom_attr['attributeId']
                if attr_id not in converted_federated_attributes.keys():
                    converted_federated_attributes[attr_id] = []
                converted_federated_attributes[attr_id].append(custom_attr['attributeValue'])

            for custom_attribute_id, values in converted_federated_attributes.items():
                mapping_attributes.append(
                    {
                        'attrId': custom_attribute_id,
                        'values': values
                    }
                )

            params = {
                'idpId': idp_id,
                'tokenDuration': token_duration,
                'mappingAttributes': mapping_attributes
            }

            return self.britive.post(self.base_url.format(id=service_identity_id), json=params)

        def unassign(self, service_identity_id: str) -> None:
            """
            Removes/deletes the service identity's assigned identity provider, along with any custom attribute mappings.

            This will revert the service identity back to use static API tokens for authentication.

            :param service_identity_id: The ID of the Service Identity.
            :returns: None.
            """
            return self.britive.delete(self.base_url.format(id=service_identity_id))

    class ScimUser:
        def __init__(self, workload):
            self.britive = workload.britive
            self.base_url: str = workload.base_url + '/scim-user/identity-provider'

        def get(self, idp_name: str) -> dict:
            """
            Gets details of the workload federation enabled service identity associated with the identity provider.

            The identity provider name provided must be a SAML identity provider.

            :param idp_name: The name of the SAML Identity Provider.
            :returns: Details of the newly assigned service identity to the identity provider.
            """

            return self.britive.get(f'{self.base_url}/{idp_name}')

        def assign(self, service_identity_id: str, idp_name: str) -> dict:
            """
            Associates a workload federation enabled service identity with an identity provider SCIM service.

            The service identity must already be configured for workload federation.
            The identity provider name provided must be a SAML identity provider.

            :param service_identity_id: The ID of the service identity.
            :param idp_name: The name of the SAML Identity Provider.
            :returns: Details of the newly assigned service identity to the identity provider.
            """

            params = {
                'idpName': idp_name,
                'userId': service_identity_id
            }

            return self.britive.post(self.base_url, json=params)

        def unassign(self, idp_name: str) -> dict:
            """
            Removes a workload federation enabled service identity from an identity provider SCIM service.

            The identity provider name provided must be a SAML identity provider.

            :param idp_name: The name of the SAML Identity Provider.
            :returns: Details of the newly assigned service identity to the identity provider.
            """

            return self.britive.delete(f'{self.base_url}/{idp_name}')
