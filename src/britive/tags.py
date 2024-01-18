
class TagMembershipRules:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/user-tags'

    def build(self, attribute_id_or_name: str, operator: str, value: str) -> dict:
        """
        Builds a membership rule.

        :param attribute_id_or_name: The attribute id or name for the rule. Names will be converted to ids by the SDK.
        :param operator: Valid values are `contains` and `is`.
        :param value: The value to match in the rule.
        :returns: Dictionary which can be used to build a list of rules.
        """

        if operator.lower() not in ['contains', 'is']:
            raise ValueError('invalid operator provided.')

        # first get list of existing identity attributes and build some helpers
        existing_attrs = [attr for attr in self.britive.identity_attributes.list()]
        existing_attr_ids = [attr['id'] for attr in existing_attrs]
        attrs_by_name = {attr['name']: attr['id'] for attr in existing_attrs}

        attribute_id = attribute_id_or_name
        if attribute_id not in existing_attr_ids:
            attribute_id = attrs_by_name.get(attribute_id_or_name, None)
        if not attribute_id:
            raise ValueError(f'identity attribute name {attribute_id_or_name} not found.')

        return {
            'attributeId': attribute_id,
            'operator': operator.lower(),
            'value': value
        }

    def list(self, tag_id: str) -> list:
        """
        List existing membership rules for the given tag.

        :param tag_id: The tag id.
        :returns: List of membership rules for the given tag.
        """

        return self.britive.get(f'{self.base_url}/{tag_id}/attribute-criteria')

    def create(self, tag_id: str, rules: list) -> list:
        """
        Create new membership rules for the given tag.

        :param tag_id: The tag id.
        :param rules: The list of rules to include in the request. Use `build` to help construct the list.
        :returns: List of newly created membership rules for the given tag.
        """

        return self.britive.post(f'{self.base_url}/{tag_id}/attribute-criteria', json=rules)

    def update(self, tag_id: str, rules: list) -> None:
        """
        Update membership rules for the given tag.

        All membership rules must be provided. What is provided in the request will fully replace the existing
        list of membership rules associated with the given tag.

        :param tag_id: The tag id.
        :param rules: The list of rules to include in the request. Use `build` to help construct the list.
        :returns: None.
        """

        return self.britive.patch(f'{self.base_url}/{tag_id}/attribute-criteria', json=rules)

    def delete(self, tag_id: str) -> None:
        """
        Delete all membership rules for the given tag.

        :param tag_id: The tag id.
        :returns: None.
        """

        return self.britive.patch(f'{self.base_url}/{tag_id}/attribute-criteria', json=[])

    def matched_users(self, tag_id: str) -> list:
        """
        Lists users which match the membership rules associated with the given tag.

        :param tag_id: The tag id.
        :returns: List of matching users.
        """

        params = {
            'page': 0,
            'size': 100
        }
        return self.britive.get(f'{self.base_url}/{tag_id}/matched-users', params=params)


class Tags:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/user-tags'
        self.membership_rules = TagMembershipRules(self.britive)

    def create(self, name: str, description: str = None, idp: str = None) -> dict:
        """
        Create a new tag.

        :param name: The tag name.
        :param description: The tag description.
        :param idp: The ID of the identity provider. To be used when creating an external tag.
        :return: Details of the newly created tag.
        """

        data = {
            'name': name,
            'description': description
        }

        if idp:
            data['userTagIdentityProviders'] = [{'identityProvider': {'id': idp}}]
            data['external'] = True

        return self.britive.post(self.base_url, json=data)

    def get(self, tag_id: str) -> dict:
        """
        Return details of a tag.

        :param tag_id: The ID of the tag.
        :return: Details of the tag.
        """

        return self.britive.get(f'{self.base_url}/{tag_id}')

    def list(self, filter_expression: str = None) -> list:
        """
        List all tags, optionally filtered via name or status.

        :param filter_expression: Filter the list of tags based on name or status. The supported operators are
            `eq' and `co`. An example is `status eq 'Active'`
        :return: List of tags.
        """

        params = {
            'page': 0,
            'size': 100
        }
        if filter_expression:
            params['filter'] = filter_expression

        return self.britive.get(self.base_url, params)

    def search(self, search_string: str) -> list:
        """
        Searche all tag fields for the given `search_string` and returns
        a list of matched tags.

        :param search_string: String to search.
        :return: List of user records.
        """

        params = {
            'page': 0,
            'size': 100,
            'searchText': search_string
        }

        return self.britive.get(self.base_url, params)

    def users_for_tag(self, tag_id: str, filter_expression: str = None) -> list:
        """
         Retrieve the details of all users assigned to a tag,

        :param tag_id: The ID of the tag.
        :param filter_expression: Filter the list of users asssigned to `tag_id` based on name or status.
        The supported operators are`eq' and `co`. An example is `status eq 'Active'`
        :return: List of users associated with `tag_id`.
        """

        params = {
            'page': 0,
            'size': 100
        }
        if filter_expression:
            params['filter'] = filter_expression

        return self.britive.get(f'{self.base_url}/{tag_id}/users', params)

    def available_users_for_tag(self, tag_id: str) -> list:
        """
        Retrieve all users available in the system that can possibly be added to a tag.

        :param tag_id: The ID of the tag.
        :return: List of users available to be assigned to `tag_id`.
        """

        return self.britive.get(f'{self.base_url}/{tag_id}/users?filter=available')

    def add_user(self, tag_id: str, user_id: str) -> dict:
        """
        Add a user to a tag.

        :param tag_id: The ID of the tag.
        :param user_id: The ID of the user.
        :return: Details of the user.
        """

        return self.britive.post(f'{self.base_url}/{tag_id}/users/{user_id}')

    def remove_user(self, tag_id: str, user_id: str) -> None:
        """
        Remove a user from a tag.

        :param tag_id: The ID of the tag.
        :param user_id: The ID of the user.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{tag_id}/users/{user_id}')

    def enable(self, tag_id: str) -> dict:
        """
        Enable a tag.

        :param tag_id: The ID of the tag.
        :return: Details of the tag.
        """

        return self.britive.post(f'{self.base_url}/{tag_id}/enabled-statuses')

    def disable(self, tag_id: str) -> dict:
        """
        Disable a tag.

        :param tag_id: The ID of the tag.
        :return: Details of the tag.
        """

        return self.britive.post(f'{self.base_url}/{tag_id}/disabled-statuses')

    def update(self, tag_id: str, name: str, description: str = None) -> dict:
        """
        Update the attributes of a tag.

        :param tag_id: The ID of the tag.
        :param name: The name of the tag.
        :param description: The description of the tag.
        :return: Details of the updated tag.
        """

        data = {
            'userTagId': tag_id,
            'name': name,
            'description': description
        }

        self.britive.patch(self.base_url, json=data)
        return self.get(tag_id)

    def delete(self, tag_id: str) -> None:
        """
        Delete a tag.

        You can delete an external tag ONLY if it has yet to be synced via SCIM.

        :param tag_id: The ID of the tag.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{tag_id}')

    def minimized_tag_details(self, tag_id: str = None, tag_ids: list = []) -> list:
        """
        Retrieve a small set of user fields given a user id.

        :param tag_id: The ID of the tag. Will be combined with `tag_ids`.
        :param tag_ids: The list of tag ids. Will be combined with `tag_id`.
        :return: List of tags with a small set of attributes.
        """
        if tag_ids is None:
            tag_ids = []
        if tag_id and tag_id not in tag_ids:
            tag_ids.append(tag_id)
        if len(tag_ids) == 0:
            return []

        return self.britive.post(f'{self.base_url}/minimized-tag-details', json=tag_ids)
