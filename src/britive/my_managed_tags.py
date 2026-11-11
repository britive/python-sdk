class MyManagedTags:
    """
    This class is meant to be called by end users. It is an API layer on top of the actions that can be performed on the
    "My Managed Tags" page of the Britive UI.

    No "administrative" access is required by the methods in this class. A user can only manage the tags they own,
    either directly or through membership of an owner tag. Calls against a tag the user does not own return 403.
    """

    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/access/user-tags'

    @staticmethod
    def _params(**kwargs) -> dict:
        return {k: v for k, v in kwargs.items() if v is not None}

    def list(
        self,
        filter_text: str = None,
        search_text: str = None,
        page: int = None,
        size: int = None,
        sort: str = None,
        headers: dict = None,
    ) -> dict:
        """
        List the tags managed by the user.

        :param filter_text: Filter expression, e.g. `name co "foo"`.
        :param search_text: Search the tag names.
        :param page: The page number to return.
        :param size: The number of results per page.
        :param sort: Sort field and direction.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: Dict with a `userTags` list and paging details.
        """

        params = self._params(filter=filter_text, searchText=search_text, page=page, size=size, sort=sort)

        return self.britive.get(f'{self.base_url}/my-managed-tags', params=params, headers=headers)

    def list_members(
        self, tag_id: str, filter_text: str = None, search_text: str = None, sort: str = None, headers: dict = None
    ) -> dict:
        """
        List the members of a managed tag.

        :param tag_id: The ID of the tag.
        :param filter_text: Filter expression.
        :param search_text: Search the members.
        :param sort: Sort field and direction.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: Dict with a `users` list and paging details.
        """

        params = self._params(filter=filter_text, searchText=search_text, sort=sort)

        return self.britive.get(f'{self.base_url}/{tag_id}/users', params=params, headers=headers)

    def list_available_members(
        self, tag_id: str, filter_text: str = None, search_text: str = None, sort: str = None, headers: dict = None
    ) -> dict:
        """
        List the active users who can be added to a managed tag.

        :param tag_id: The ID of the tag.
        :param filter_text: Filter expression.
        :param search_text: Search the users.
        :param sort: Sort field and direction.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: Dict with a `users` list and paging details.
        """

        params = self._params(filter=filter_text, searchText=search_text, sort=sort)

        return self.britive.get(f'{self.base_url}/{tag_id}/available-users', params=params, headers=headers)

    def add_member(self, tag_id: str, user_id: str, headers: dict = None) -> dict:
        """
        Add a user to a managed tag.

        :param tag_id: The ID of the tag.
        :param user_id: The ID of the user.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: Details of the added user.
        """

        return self.britive.post(f'{self.base_url}/{tag_id}/users/{user_id}', json={'userId': user_id}, headers=headers)

    def remove_member(self, tag_id: str, user_id: str, headers: dict = None) -> None:
        """
        Remove a user from a managed tag.

        :param tag_id: The ID of the tag.
        :param user_id: The ID of the user.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{tag_id}/users/{user_id}', headers=headers)

    def get_attribute_criteria(self, tag_id: str, headers: dict = None) -> list:
        """
        Return the attribute based membership criteria of a managed tag.

        :param tag_id: The ID of the tag.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: List of attribute criteria.
        """

        return self.britive.get(f'{self.base_url}/{tag_id}/attribute-criteria', headers=headers)

    def add_attribute_criteria(self, tag_id: str, criteria: list, headers: dict = None) -> list:
        """
        Add attribute based membership criteria to a managed tag.

        :param tag_id: The ID of the tag.
        :param criteria: List of criteria, each with `attributeId`, `operator` and `value`.
            Example:
                [{"attributeId": "...", "operator": "is", "value": "engineering"}]
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: List of the tag's attribute criteria.
        """

        return self.britive.post(f'{self.base_url}/{tag_id}/attribute-criteria', json=criteria, headers=headers)

    def update_attribute_criteria(self, tag_id: str, criteria: list, headers: dict = None) -> None:
        """
        Replace the attribute based membership criteria of a managed tag.

        :param tag_id: The ID of the tag.
        :param criteria: List of criteria, each with `attributeId`, `operator` and `value`, and the `id` of an existing
            criterion when updating it.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: None. An empty `criteria` list removes all criteria.
        """

        return self.britive.patch(f'{self.base_url}/{tag_id}/attribute-criteria', json=criteria, headers=headers)

    def list_matched_members(
        self, tag_id: str, filter_text: str = None, search_text: str = None, headers: dict = None
    ) -> dict:
        """
        List the users who match the attribute based membership criteria of a managed tag.

        :param tag_id: The ID of the tag.
        :param filter_text: Filter expression, e.g. `status eq active`.
        :param search_text: Search the users.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: Dict with a `users` list and paging details.
        """

        params = self._params(filter=filter_text, searchText=search_text)

        return self.britive.get(f'{self.base_url}/{tag_id}/matched-users', params=params, headers=headers)

    def list_identity_attributes(self, headers: dict = None) -> list:
        """
        List the identity attributes that membership criteria can match on.

        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: List of identity attributes.
        """

        return self.britive.get(f'{self.britive.base_url}/access/users/attributes', headers=headers)

    def list_requested_memberships(
        self, tag_id: str, filter_text: str = None, search_text: str = None, headers: dict = None
    ) -> dict:
        """
        List the users whose membership of a managed tag was granted through an access request.

        :param tag_id: The ID of the tag.
        :param filter_text: Filter expression.
        :param search_text: Search the users.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: Dict with a `users` list and paging details.
        """

        params = self._params(filter=filter_text, searchText=search_text)

        return self.britive.get(f'{self.base_url}/{tag_id}/requested-memberships', params=params, headers=headers)

    def remove_requested_membership(self, tag_id: str, user_id: str, headers: dict = None) -> None:
        """
        Remove a user's requested membership of a managed tag.

        If the request was the user's only path to membership, the user is removed from the tag.

        :param tag_id: The ID of the tag.
        :param user_id: The ID of the user.
        :param headers: Any additional headers
            Example:
                {
                    "X-On-Behalf-Of": "Bearer ... | user@... | username",
                    ...
                }
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{tag_id}/requested-memberships/{user_id}', headers=headers)
