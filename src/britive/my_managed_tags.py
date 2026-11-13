class MyManagedTags:
    """Self-service membership management for tags owned by the authenticated identity.

    Ownership can be direct or through membership of an owner tag. The API rejects non-owners with 403.
    List methods preserve the API's summary dictionary, with records under `data`. Without explicit paging,
    the managed-tag API returns all matching records. Supplying both `page` and `size` selects one page.
    """

    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/access/user-tags'

    def _list(
        self,
        path: str,
        *,
        filter_text: str = None,
        search_text: str = None,
        sort: str = None,
        page: int = None,
        size: int = None,
        headers: dict = None,
    ) -> dict:
        if (page is None) != (size is None):
            raise ValueError('page and size must be provided together.')
        if page is not None:
            if isinstance(page, bool) or not isinstance(page, int) or page < 0:
                raise ValueError('page must be a non-negative integer.')
            if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
                raise ValueError('size must be a positive integer.')
        params = {'filter': filter_text, 'searchText': search_text, 'sort': sort, 'page': page, 'size': size}
        # Unpaged summaries can have size=0 and page=0. Preserve them instead of auto-paginating forever.
        return self.britive.get(
            f'{self.base_url}/{path}',
            params={k: v for k, v in params.items() if v is not None},
            headers=headers,
            pagination='none',
        )

    def list(
        self,
        filter_text: str = None,
        search_text: str = None,
        page: int = None,
        size: int = None,
        sort: str = None,
        headers: dict = None,
    ) -> dict:
        """List tags managed by the user.

        :param filter_text: Filter expression, such as `name co "foo"`.
        :param search_text: Search tag names.
        :param page: Zero-based page number, supplied with `size`; omit both to return all matches.
        :param size: Positive page size, supplied with `page`.
        :param sort: Sort field and direction, applied when paging, such as `name,asc`.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: API summary with a `data` list and paging details. Does not auto-paginate.
        """
        return self._list(
            'my-managed-tags',
            filter_text=filter_text,
            search_text=search_text,
            page=page,
            size=size,
            sort=sort,
            headers=headers,
        )

    def list_members(
        self,
        tag_id: str,
        filter_text: str = None,
        search_text: str = None,
        sort: str = None,
        headers: dict = None,
        *,
        page: int = None,
        size: int = None,
    ) -> dict:
        """List members of a managed tag.

        :param tag_id: The ID of the tag.
        :param filter_text: Filter expression.
        :param search_text: Search the members.
        :param sort: Sort field and direction, applied when paging.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :param page: Zero-based page number, supplied with `size`; omit both to return all matches.
        :param size: Positive page size, supplied with `page`.
        :return: API summary with a `data` list and paging details. Does not auto-paginate.
        """
        return self._list(
            f'{tag_id}/users',
            filter_text=filter_text,
            search_text=search_text,
            sort=sort,
            page=page,
            size=size,
            headers=headers,
        )

    def list_available_members(
        self,
        tag_id: str,
        filter_text: str = None,
        search_text: str = None,
        sort: str = None,
        headers: dict = None,
        *,
        page: int = None,
        size: int = None,
    ) -> dict:
        """List active users who can be added to a managed tag.

        :param tag_id: The ID of the tag.
        :param filter_text: Filter expression.
        :param search_text: Search the users.
        :param sort: Sort field and direction, applied when paging.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :param page: Zero-based page number, supplied with `size`; omit both to return all matches.
        :param size: Positive page size, supplied with `page`.
        :return: API summary with a `data` list and paging details. Does not auto-paginate.
        """
        return self._list(
            f'{tag_id}/available-users',
            filter_text=filter_text,
            search_text=search_text,
            sort=sort,
            page=page,
            size=size,
            headers=headers,
        )

    def add_member(self, tag_id: str, user_id: str, headers: dict = None) -> dict:
        """Add a user to a managed tag.

        :param tag_id: The ID of the tag.
        :param user_id: The ID of the user.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: Details of the added user.
        """
        return self.britive.post(f'{self.base_url}/{tag_id}/users/{user_id}', json={'userId': user_id}, headers=headers)

    def remove_member(self, tag_id: str, user_id: str, headers: dict = None) -> None:
        """Remove a user from a managed tag.

        :param tag_id: The ID of the tag.
        :param user_id: The ID of the user.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: None.
        """
        return self.britive.delete(f'{self.base_url}/{tag_id}/users/{user_id}', headers=headers)

    def get_attribute_criteria(self, tag_id: str, headers: dict = None) -> list:
        """Return a managed tag's attribute-based membership criteria.

        :param tag_id: The ID of the tag.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: List of criteria.
        """
        return self.britive.get(f'{self.base_url}/{tag_id}/attribute-criteria', headers=headers)

    def add_attribute_criteria(self, tag_id: str, criteria: list, headers: dict = None) -> list:
        """Add attribute-based membership criteria to a managed tag.

        :param tag_id: The ID of the tag.
        :param criteria: List of criteria with `attributeId`, `operator`, and `value`.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: List of the tag's attribute criteria.
        """
        return self.britive.post(f'{self.base_url}/{tag_id}/attribute-criteria', json=criteria, headers=headers)

    def update_attribute_criteria(self, tag_id: str, criteria: list, headers: dict = None) -> None:
        """Replace a managed tag's attribute-based membership criteria.

        :param tag_id: The ID of the tag.
        :param criteria: Complete replacement list, with `attributeId`, `operator`, `value`, and the `id` of an
            existing criterion when updating it. An empty list removes all criteria.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: None.
        """
        return self.britive.patch(f'{self.base_url}/{tag_id}/attribute-criteria', json=criteria, headers=headers)

    def list_matched_members(
        self,
        tag_id: str,
        filter_text: str = None,
        search_text: str = None,
        headers: dict = None,
        *,
        page: int = None,
        size: int = None,
        sort: str = None,
    ) -> dict:
        """List users matching a managed tag's attribute criteria.

        :param tag_id: The ID of the tag.
        :param filter_text: Filter expression, such as `status eq active`.
        :param search_text: Search the users.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :param page: Zero-based page number, supplied with `size`; omit both to return all matches.
        :param size: Positive page size, supplied with `page`.
        :param sort: Sort field and direction, applied when paging.
        :return: API summary with a `data` list and paging details. Does not auto-paginate.
        """
        return self._list(
            f'{tag_id}/matched-users',
            filter_text=filter_text,
            search_text=search_text,
            page=page,
            size=size,
            sort=sort,
            headers=headers,
        )

    def list_identity_attributes(self, headers: dict = None) -> list:
        """List identity attributes available to membership criteria.

        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: List of identity attributes.
        """
        return self.britive.get(f'{self.britive.base_url}/access/users/attributes', headers=headers)

    def list_requested_memberships(
        self,
        tag_id: str,
        filter_text: str = None,
        search_text: str = None,
        headers: dict = None,
        *,
        page: int = None,
        size: int = None,
        sort: str = None,
    ) -> dict:
        """List users whose tag membership was granted through an access request.

        :param tag_id: The ID of the tag.
        :param filter_text: Filter expression.
        :param search_text: Search the users.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :param page: Zero-based page number, supplied with `size`; omit both to return all matches.
        :param size: Positive page size, supplied with `page`.
        :param sort: Sort field and direction, applied when paging.
        :return: API summary with a `data` list and paging details. Does not auto-paginate.
        """
        return self._list(
            f'{tag_id}/requested-memberships',
            filter_text=filter_text,
            search_text=search_text,
            page=page,
            size=size,
            sort=sort,
            headers=headers,
        )

    def remove_requested_membership(self, tag_id: str, user_id: str, headers: dict = None) -> None:
        """Remove a user's requested membership of a managed tag.

        If the request was the user's only path to membership, the API removes the user from the tag.

        :param tag_id: The ID of the tag.
        :param user_id: The ID of the user.
        :param headers: Additional headers, including `X-On-Behalf-Of` for delegated requests.
        :return: None.
        """
        return self.britive.delete(f'{self.base_url}/{tag_id}/requested-memberships/{user_id}', headers=headers)
