
class Tags:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/user-tags'

    def create(self, name: str, description: str = None) -> dict:
        """
        Create a new tag

        :param name: The tag name.
        :param description: The tag description.
        :return: Details of the newly created tag.
        """

        data = {
            'name': name,
            'description': description
        }

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

        :param tag_id: The ID of the tag.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{tag_id}')

