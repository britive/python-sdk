
class CustomAttributes:
    def __init__(self, principal):
        self.britive = principal.britive
        self.base_url: str = principal.britive.base_url + '/users/{id}/custom-attributes'  # will .format(id=...) later

    def get(self, principal_id: str, as_dict: bool = False) -> any:
        """
        Retrieve the current custom attributes associated with the specified Service Identity or User.

        :param principal_id: The ID of the Service Identity or User.
        :param as_dict: Whether to return a key/value mapping vs the raw response which is a list.
        """
        response = self.britive.get(self.base_url.format(id=principal_id))
        if as_dict:
            attrs = {}
            for attribute in response:
                current_attr_id = attribute['attributeId']
                if current_attr_id in attrs.keys():  # need to handle the multi-value attributes
                    is_list = isinstance(attrs[attribute['attributeId']], list)

                    if not is_list:  # make it a list
                        attrs[current_attr_id] = [attrs[current_attr_id]]
                    attrs[current_attr_id].append(attribute['attributeValue'])
                else:
                    attrs[current_attr_id] = attribute['attributeValue']
            return attrs
        else:
            return response

    def add(self, principal_id: str, custom_attributes: dict) -> None:
        """
        Adds custom attribute mappings to the provided Service Identity or User.

        :param principal_id: The IDs of the Service Identity or User.
        :param custom_attributes: An attribute map where keys are the custom attribute ids or names and values are
            custom attribute values as strings or list of strings for multivalued attributes.
        """
        return self._modify(
            principal_id=principal_id,
            operation='add',
            custom_attributes=custom_attributes,
        )

    def remove(self, principal_id: str, custom_attributes: dict) -> None:
        """
        Removes custom attribute mapping from the provided Service Identity or User.

        :param principal_id: The IDs of the Service Identity or User.
        :param custom_attributes: An attribute map where keys are the custom attribute ids or names and values are
            custom attribute values as strings or list of strings for multivalued attributes.
        """
        return self._modify(
            principal_id=principal_id,
            operation='remove',
            custom_attributes=custom_attributes
        )

    def _build_list(self, operation: str, custom_attributes: dict):
        # first get list of existing custom identity attributes and build some helpers
        existing_attrs = [attr for attr in self.britive.identity_attributes.list() if not attr['builtIn']]
        existing_attr_ids = [attr['id'] for attr in existing_attrs]
        attrs_by_name = {attr['name']: attr['id'] for attr in existing_attrs}

        # for each custom_attribute key/value provided ensure we convert to ID and build the list
        attrs_list = []
        for id_or_name, value in custom_attributes.items():
            # obtain the custom attribute id
            custom_attribute_id = id_or_name
            if custom_attribute_id not in existing_attr_ids:
                custom_attribute_id = attrs_by_name.get(custom_attribute_id, None)
            if not custom_attribute_id:
                raise ValueError(f'custom identity attribute name {id_or_name} not found.')

            # and create the list dict entry for each value
            value = value if isinstance(value, list) else [value]  # handle multivalued attributes
            for v in value:
                attrs_list.append(
                    {
                        'op': operation,
                        'customUserAttribute': {
                            'attributeValue': v,
                            'attributeId': custom_attribute_id
                        }
                    }
                )
        return attrs_list

    def _modify(self, principal_id: str, operation: str, custom_attributes: dict) -> None:
        if operation not in ['add', 'remove']:
            raise ValueError('operation must either be add or remove')

        return self.britive.patch(
            self.base_url.format(id=principal_id),
            json=self._build_list(operation=operation, custom_attributes=custom_attributes)
        )
