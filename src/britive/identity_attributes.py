
class IdentityAttributes:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/users/attributes'

    def list(self):
        """
        Return a list of identity attributes.

        :return: List of identity attributes.
        """

        return self.britive.get(self.base_url)

    def create(self, name: str, description: str, data_type: str, multi_valued: bool) -> dict:
        """
        Create a new identity attribute.

        :param name: The name of the identity attribute.
        :param description: The description of the identity attribute.
        :param data_type: The data type of the identity attribute. Valid values are
            `String`, `Number`, 'Boolean`, 'Date`.
        :param multi_valued: Whether the attribute should be considered multi-valued.
        :return: Details of the newly created identity attribute.
        """

        if data_type not in ['String', 'Number', 'Boolean', 'Date']:
            raise ValueError(f'invalid data_type {data_type}')

        data = {
            'name': name,
            'description': description,
            'dataType': data_type,
            'multiValued': multi_valued
        }

        return self.britive.post(self.base_url, json=data)

    def delete(self, attribute_id: str) -> None:
        """
        Delete the specified identity attribute.

        :param attribute_id: The ID of the identity attribute to delete.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{attribute_id}')
