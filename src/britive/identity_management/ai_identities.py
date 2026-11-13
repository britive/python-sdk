from ._identities import _Identities, _IdentityTokens


class AIIdentities(_Identities):
    """AI identity operations with AI-specific public parameters."""

    def __init__(self, britive) -> None:
        super().__init__(britive, identity_type='AIIdentity')

    def get(self, ai_identity_id: str) -> dict:
        """Return an AI identity.

        :param ai_identity_id: The ID of the AI identity.
        :return: Identity details.
        :raises NotFound: if the identity does not exist or is not an AI identity.
        """
        return self._get(ai_identity_id)

    def update(self, ai_identity_id: str, **kwargs) -> dict:
        """Update an AI identity.

        :param ai_identity_id: The ID of the AI identity.
        :param kwargs: API fields including `name`, `description`, `businessUse`, `jobFunction`,
            `managerId`, `attributes`, and `relationships`. Use `enable` and `disable` to change status.
            The API treats `attributes` as a replacement list and replaces each supplied relationship group.
        :return: Updated identity details.
        :raises NotFound: if `name` is omitted and the identity does not exist or is not an AI identity.
        :raises DoesNotExistError: if `name` is supplied and the identity does not exist.
        :raises UserUpdateError: if `name` is supplied and the identity is not an AI identity. Nothing is changed.
        """
        return self._update(ai_identity_id, **kwargs)

    def delete(self, ai_identity_id: str) -> None:
        """Delete an AI identity.

        :param ai_identity_id: The ID of the AI identity.
        :raises NotFound: if the identity does not exist or is not an AI identity.
        """
        self._delete(ai_identity_id)

    def minimized_identity_details(self, ai_identity_id: str = None, ai_identity_ids: list = None) -> list:
        """Return a small set of identity fields.

        :param ai_identity_id: Identity ID to combine with the list.
        :param ai_identity_ids: List of identity IDs.
        :return: Minimized records. The API does not filter by type and omits unknown IDs.
        """
        return self._minimized_details(ai_identity_id, ai_identity_ids)

    def enable(self, ai_identity_id: str = None, ai_identity_ids: list = None) -> object:
        """Enable AI identities, merging the single ID with the list when both are provided.

        :param ai_identity_id: The ID of the AI identity to enable.
        :param ai_identity_ids: List of AI identity IDs to enable. Usernames are not accepted.
        :return: A list when the ID list is non-empty, otherwise an identity dict.
        :raises ValueError: if no IDs are provided or IDs are invalid.
        :raises NotFound: without an ID list, if the identity does not exist or is not an AI identity.
        :raises DoesNotExistError: with an ID list, if any identity does not exist or is not an AI identity.
        """
        return self._set_status('enabled', ai_identity_id, ai_identity_ids)

    def disable(self, ai_identity_id: str = None, ai_identity_ids: list = None) -> object:
        """Disable AI identities, merging the single ID with the list when both are provided.

        :param ai_identity_id: The ID of the AI identity to disable.
        :param ai_identity_ids: List of AI identity IDs to disable. Usernames are not accepted.
        :return: A list when the ID list is non-empty, otherwise an identity dict.
        :raises ValueError: if no IDs are provided or IDs are invalid.
        :raises NotFound: without an ID list, if the identity does not exist or is not an AI identity.
        :raises DoesNotExistError: with an ID list, if any identity does not exist or is not an AI identity.
        """
        return self._set_status('disabled', ai_identity_id, ai_identity_ids)


class AIIdentityTokens(_IdentityTokens):
    """Token operations with AI-specific public parameters."""

    def create(self, ai_identity_id: str, token_expiration_days: int = 90) -> dict:
        """Create an AI identity token, replacing its existing token.

        The token has the identity's privileges and is returned only once.

        :param ai_identity_id: The ID of the AI identity.
        :param token_expiration_days: Token inactivity lifetime, between 1 and 90 days.
        :return: Created token details.
        """
        return self._create(ai_identity_id, token_expiration_days)

    def update(self, ai_identity_id: str, token_expiration_days: int = 90) -> None:
        """Update the inactivity lifetime of an AI identity token without replacing it.

        :param ai_identity_id: The ID of the AI identity.
        :param token_expiration_days: Token inactivity lifetime, between 1 and 90 days.
        :return: None. Use `get` to retrieve the updated token metadata.
        """
        return self._update(ai_identity_id, token_expiration_days)

    def get(self, ai_identity_id: str) -> dict:
        """Return token details for an AI identity.

        :param ai_identity_id: The ID of the AI identity.
        :return: Token details.
        """
        return self._get(ai_identity_id)
