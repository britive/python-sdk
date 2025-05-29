class SessionAttributes:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/paps'

    def add_static(self, profile_id: str, tag_name: str, tag_value: str, transitive: bool = False) -> dict:
        """
        AWS ONLY - Add a static session attribute to the profile.

        :param profile_id: The ID of the profile.
        :param tag_name: The name of the session tag to include in the AssumeRoleWithSAML call.
        :param tag_value: The value of the session tag to include in the AssumeRoleWithSAML call.
        :param transitive: Set to True to mark the session tag as transitive. Review AWS documentation on why you
            may or may not want this.
        :return: Details of added attribute.
        """

        data = {
            'sessionAttributeType': 'Static',
            'transitive': transitive,
            'attributeSchemaId': None,
            'mappingName': tag_name,
            'attributeValue': tag_value,
        }

        return self.britive.post(f'{self.base_url}/{profile_id}/session-attributes', json=data)

    def add_dynamic(self, profile_id: str, identity_attribute_id: str, tag_name: str, transitive: bool = False) -> dict:
        """
        AWS ONLY - Add a dynamic session attribute to the profile.

        The value will be sourced from the identity attribute specified.

        :param profile_id: The ID of the profile.
        :param identity_attribute_id: The ID of the identity attribute.
            Call `britive.identity_management.identity_attributes.list()` for which attributes can be provided.
        :param tag_name: The name of the session tag to include in the AssumeRoleWithSAML call. The value will be
            dynamically determined based on the value of the specified identity attribute.
        :param transitive: Set to True to mark the session tag as transitive. Review AWS documentation on why you
            may or may not want this.
        :return: Details of added attribute.
        """

        data = {
            'sessionAttributeType': 'Identity',
            'transitive': transitive,
            'attributeSchemaId': identity_attribute_id,
            'mappingName': tag_name,
            'attributeValue': None,
        }

        return self.britive.post(f'{self.base_url}/{profile_id}/session-attributes', json=data)

    def update_static(
        self, profile_id: str, attribute_id, tag_name: str, tag_value: str, transitive: bool = False
    ) -> None:
        """
        AWS ONLY - Update the static session attribute to the profile.

        :param profile_id: The ID of the profile.
        :param attribute_id: The ID of the session attribute to update.
        :param tag_name: The name of the session tag to include in the AssumeRoleWithSAML call.
        :param tag_value: THe value of the session tag to include in the AssumeRoleWithSAML call.
        :param transitive: Set to True to mark the session tag as transitive. Review AWS documentation on why you
            may or may not want this.
        :return: None.
        """

        data = {
            'sessionAttributeType': 'Static',
            'transitive': transitive,
            'attributeSchemaId': None,
            'mappingName': tag_name,
            'attributeValue': tag_value,
            'id': attribute_id,
        }

        return self.britive.put(f'{self.base_url}/{profile_id}/session-attributes', json=data)

    def update_dynamic(
        self, profile_id: str, attribute_id: str, identity_attribute_id: str, tag_name: str, transitive: bool = False
    ) -> dict:
        """
        AWS ONLY - Update the dynamic session attribute to the profile.

        :param profile_id: The ID of the profile.
        :param attribute_id: The ID of the session attribute to update.
        :param identity_attribute_id: The ID of the identity attribute.
            Call `britive.identity_management.identity_attributes.list()` for which attributes can be provided.
        :param tag_name: The name of the session tag to include in the AssumeRoleWithSAML call. The value will be
            dynamically determined based on the value of the specified identity attribute.
        :param transitive: Set to True to mark the session tag as transitive. Review AWS documentation on why you
            may or may not want this.
        :return: Details of added attribute.
        """

        data = {
            'sessionAttributeType': 'Identity',
            'transitive': transitive,
            'attributeSchemaId': identity_attribute_id,
            'mappingName': tag_name,
            'attributeValue': None,
            'id': attribute_id,
        }

        return self.britive.put(f'{self.base_url}/{profile_id}/session-attributes', json=data)

    def list(self, profile_id: str) -> list:
        """
        Return a list of session attributes associated with the profile.

        :param profile_id: The ID of the profile.
        :return: List of session attributes associated with the profile.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}/session-attributes')

    def remove(self, profile_id: str, attribute_id: str) -> None:
        """
        Remove an attribute from the profile.

        :param profile_id: The ID of the profile.
        :param attribute_id: The ID of the session attribute.
        :return: None.
        """

        return self.britive.delete(f'{self.base_url}/{profile_id}/session-attributes/{attribute_id}')
