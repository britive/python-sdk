import builtins

from .identity_attributes import CustomAttributes

_VALID_STATUSES = ['active', 'inactive']


def _validate_identity_id(identity_id: str) -> None:
    if not isinstance(identity_id, str) or not identity_id.strip():
        raise ValueError('Identity IDs must be non-empty strings.')


def _collect_identity_ids(identity_id: str = None, identity_ids: list = None) -> list:
    if identity_ids is not None and not isinstance(identity_ids, list):
        raise ValueError('identity_ids must be a list of non-empty strings.')
    identities = list(identity_ids or [])
    if identity_id is not None:
        identities.append(identity_id)
    for value in identities:
        _validate_identity_id(value)
    return list(dict.fromkeys(identities))


class _Identities:
    """Shared request implementation for typed identity collections."""

    def __init__(self, britive, identity_type: str) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/users'
        self.custom_attributes = CustomAttributes(britive)
        self.identity_type = identity_type

    def list(self, filter_expression: str = None, include_tags: bool = False, *, search_string: str = None) -> list:
        """Return identities of this collection's type.

        :param filter_expression: Filter by name, status, or role using `eq` or `co`.
        :param include_tags: Include tags and group memberships.
        :param search_string: Search all identity fields.
        :return: List of matching identity records.
        """
        params = {'type': self.identity_type, 'page': 0, 'size': 100}
        if filter_expression:
            params['filter'] = filter_expression
        if search_string is not None:
            params['searchText'] = search_string
        if include_tags:
            params['includeTags'] = 'true'
        return self.britive.get(self.base_url, params=params)

    def get_by_name(self, name: str) -> builtins.list:
        """Return identities whose name contains `name`."""
        return self.list(filter_expression=f'name co "{name}"')

    def get_by_status(self, status: str) -> builtins.list:
        """Return identities with an `active` or `inactive` status."""
        if status not in _VALID_STATUSES:
            raise ValueError(f'status {status} not allowed.')
        return self.list(filter_expression=f'status eq "{status}"')

    def search(self, search_string: str) -> builtins.list:
        """Search all identity fields within this collection's type."""
        return self.list(search_string=search_string)

    def create(self, **kwargs) -> dict:
        """Create an identity of this collection's type.

        :param kwargs: Identity fields. `name` is required. Optional fields include `description`, `status`,
            `businessUse`, `jobFunction`, `managerId`, `attributes`, and `relationships`.
            Service identity creation also supports `category`; AI identity creation does not persist it.
            Status must be `active` or `inactive` and defaults to `active`. Relationships are grouped under
            `managers`, `owners`, or `delegates`. Entries use `relatedEntityType` (`User` or `Tag`) and
            `relatedEntityId` or `relatedEntityName`. API validation determines which values are accepted.
        :return: Created identity record.
        """
        return self._create(kwargs, required_fields=['name'])

    def _create(self, fields: dict, *, required_fields: builtins.list) -> dict:
        fields = dict(fields)
        fields['type'] = self.identity_type
        if 'status' not in fields:
            fields['status'] = 'active'
        if fields['status'] not in _VALID_STATUSES:
            raise ValueError(f'invalid status {fields["status"]}')
        if not all(field in fields for field in required_fields):
            raise ValueError('Not all required keyword arguments were provided.')
        return self.britive.post(self.base_url, json=fields)

    def _get(self, identity_id: str) -> dict:
        _validate_identity_id(identity_id)
        return self.britive.get(f'{self.base_url}/{identity_id}', params={'type': self.identity_type})

    def _prepare_update(self, identity_id: str, fields: dict) -> dict:
        if 'name' not in fields:
            existing = self._get(identity_id)
            fields['name'] = existing['name']
        fields['roleName'] = ''
        return fields

    def _update(self, identity_id: str, **kwargs) -> dict:
        _validate_identity_id(identity_id)
        kwargs = self._prepare_update(identity_id, kwargs)
        kwargs['type'] = self.identity_type
        self.britive.patch(f'{self.base_url}/{identity_id}', json=kwargs)
        return self._get(identity_id)

    def _delete(self, identity_id: str) -> None:
        _validate_identity_id(identity_id)
        self.britive.delete(f'{self.base_url}/{identity_id}', params={'type': self.identity_type})

    def _minimized_details(self, identity_id: str = None, identity_ids: builtins.list = None) -> builtins.list:
        # This endpoint accepts all identity types and has no type constraint.
        identities = _collect_identity_ids(identity_id, identity_ids)
        if not identities:
            return []
        return self.britive.post(f'{self.base_url}/minimized-user-details', json=identities)

    def _set_status(self, status: str, identity_id: str = None, identity_ids: builtins.list = None) -> object:
        computed_identities = _collect_identity_ids(identity_id, identity_ids)
        if not computed_identities:
            raise ValueError('identity_id or identity_ids is required.')

        params = {'type': self.identity_type}
        if not identity_ids:
            return self.britive.post(f'{self.base_url}/{identity_id}/{status}-statuses', params=params)

        return self.britive.post(f'{self.base_url}/{status}-statuses', params=params, json=computed_identities)


class _IdentityTokens:
    """Shared token requests for non-human identities."""

    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}'

    @staticmethod
    def _validate_token_expiration(days: int) -> None:
        if isinstance(days, bool) or not isinstance(days, int) or not (1 <= days <= 90):
            raise ValueError('Token expiration must be an integer between 1 and 90 days.')

    def _create(self, identity_id: str, token_expiration_days: int = 90) -> dict:
        _validate_identity_id(identity_id)
        self._validate_token_expiration(token_expiration_days)
        data = {'tokenExpirationDays': token_expiration_days}
        return self.britive.post(f'{self.base_url}/users/{identity_id}/tokens', json=data)

    def _update(self, identity_id: str, token_expiration_days: int = 90) -> None:
        _validate_identity_id(identity_id)
        self._validate_token_expiration(token_expiration_days)
        data = {'tokenExpirationDays': token_expiration_days}
        self.britive.patch(f'{self.base_url}/users/{identity_id}/tokens', json=data)

    def _get(self, identity_id: str) -> dict:
        _validate_identity_id(identity_id)
        return self.britive.get(f'{self.base_url}/users/{identity_id}/tokens')
