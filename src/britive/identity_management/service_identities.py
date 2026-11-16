from ._identities import _Identities, _IdentityTokens


class ServiceIdentities(_Identities):
    """Service identity operations with service-specific public parameters."""

    def __init__(self, britive) -> None:
        super().__init__(britive, identity_type='ServiceIdentity')

    def get(self, service_identity_id: str) -> dict:
        """Return a service identity.

        :param service_identity_id: The ID of the service identity.
        :return: Identity details.
        :raises NotFound: if the identity does not exist or has the wrong type.
        """
        return self._get(service_identity_id)

    def update(self, service_identity_id: str, **kwargs) -> dict:
        """Update a service identity.

        :param service_identity_id: The ID of the service identity.
        :param kwargs: API fields including `name`, `description`, `businessUse`, `jobFunction`, `category`,
            `managerId`, `attributes`, and `relationships`. Use `enable` and `disable` to change status.
            The API treats `attributes` as a replacement list and replaces each supplied relationship group.
        :return: Updated identity details.
        :raises NotFound: if `name` is omitted and the identity does not exist or has the wrong type.
        :raises DoesNotExistError: if `name` is supplied and the identity does not exist.
        :raises UserUpdateError: if `name` is supplied and the identity has the wrong type. Nothing is changed.
        """
        return self._update(service_identity_id, **kwargs)

    def delete(self, service_identity_id: str) -> None:
        """Delete a service identity.

        :param service_identity_id: The ID of the service identity.
        :raises NotFound: if the identity does not exist or has the wrong type.
        """
        self._delete(service_identity_id)

    def minimized_identity_details(self, service_identity_id: str = None, service_identity_ids: list = None) -> list:
        """Return a small set of identity fields.

        :param service_identity_id: Identity ID to combine with the list.
        :param service_identity_ids: List of identity IDs.
        :return: Minimized records. The API does not filter by type and omits unknown IDs.
        """
        return self._minimized_details(service_identity_id, service_identity_ids)

    def enable(self, service_identity_id: str = None, service_identity_ids: list = None) -> object:
        """Enable service identities, merging the single ID with the list when both are provided.

        :param service_identity_id: The ID of the service identity to enable.
        :param service_identity_ids: List of service identity IDs to enable. Usernames are not accepted.
        :return: A list when `service_identity_ids` is non-empty, otherwise an identity dict.
        :raises ValueError: if no IDs are provided or IDs are invalid.
        :raises NotFound: without an ID list, if the identity does not exist or has the wrong type.
        :raises DoesNotExistError: with an ID list, if any identity does not exist or has the wrong type.
        """
        return self._set_status('enabled', service_identity_id, service_identity_ids)

    def disable(self, service_identity_id: str = None, service_identity_ids: list = None) -> object:
        """Disable service identities, merging the single ID with the list when both are provided.

        :param service_identity_id: The ID of the service identity to disable.
        :param service_identity_ids: List of service identity IDs to disable. Usernames are not accepted.
        :return: A list when `service_identity_ids` is non-empty, otherwise an identity dict.
        :raises ValueError: if no IDs are provided or IDs are invalid.
        :raises NotFound: without an ID list, if the identity does not exist or has the wrong type.
        :raises DoesNotExistError: with an ID list, if any identity does not exist or has the wrong type.
        """
        return self._set_status('disabled', service_identity_id, service_identity_ids)


class ServiceIdentityTokens(_IdentityTokens):
    """Token operations with the existing service identity parameter names."""

    def create(self, service_identity_id: str, token_expiration_days: int = 90) -> dict:
        """Create a service identity token, replacing its existing token.

        The token has the identity's privileges and is returned only once.

        :param service_identity_id: The ID of the service identity.
        :param token_expiration_days: Token inactivity lifetime, between 1 and 90 days.
        :return: Created token details.
        """
        return self._create(service_identity_id, token_expiration_days)

    def update(self, service_identity_id: str, token_expiration_days: int = 90) -> None:
        """Update the inactivity lifetime of a service identity token without replacing it.

        :param service_identity_id: The ID of the service identity.
        :param token_expiration_days: Token inactivity lifetime, between 1 and 90 days.
        :return: None. Use `get` to retrieve the updated token metadata.
        """
        return self._update(service_identity_id, token_expiration_days)

    def get(self, service_identity_id: str) -> dict:
        """Return token details for a service identity.

        :param service_identity_id: The ID of the service identity.
        :return: Token details.
        """
        return self._get(service_identity_id)
