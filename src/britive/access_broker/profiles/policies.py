class Policies:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/profiles'

    def list(self, profile_id: str) -> None:
        """
        Retrieve all policies for a profile.

        :param profile_id: ID of the profile.
        :return: List of policies.
        """
        return self.britive.get(f'{self.base_url}/{profile_id}/policies')

    def create(
        self,
        profile_id: str,
        name: str,
        access_type: str,
        condition: dict = None,
        members: list = None,
        is_active: bool = True,
        is_draft: bool = False,
        is_read_only: bool = False,
        resource_labels: dict = None,
    ) -> dict:
        """
        Create a new policy.

        :param profile_id: ID of the profile.
        :param name: Name of the policy.
        :param access_type: Access type of the policy.
        :param condition: Condition of the policy.
        :param members: Dict of member type objects.
            Example: {
                users: [
                    {'id': '...'}
                ],
                tags: [
                    {'id': '...'}
                ],
                tokens: [
                    {'id': '...'}
                ],
                serviceIdentities: [
                    {'id': '...'}
                ],
            }
        :param is_active: Is active.
        :param is_draft: Is draft.
        :param is_read_only: Is read only.
        :param resource_labels: Resource labels.
            Example: {
                'additionalProp1': [
                    'string',
                ],
                ...
            }
        :return: Created policy.
        """
        if condition is None:
            condition = {}
        if members is None:
            members = []
        if resource_labels is None:
            resource_labels = {}

        params = {
            'name': name,
            'accessType': access_type,
            'condition': condition,
            'isActive': is_active,
            'isDraft': is_draft,
            'isReadOnly': is_read_only,
            'resourceLabels': resource_labels,
            'members': members,
        }
        return self.britive.post(f'{self.base_url}/{profile_id}/policies', json=params)

    def get(self, profile_id: str, policy_id: str) -> dict:
        """
        Retrieve a policy by ID.

        :param profile_id: ID of the profile.
        :param policy_id: ID of the policy.
        :return: Policy.
        """

        return self.britive.get(f'{self.base_url}/{profile_id}/policies/{policy_id}')

    def update(
        self,
        profile_id: str,
        policy_id: str,
        name: str,
        access_type: str,
        condition: dict = None,
        members: list = None,
        is_active: bool = True,
        is_draft: bool = False,
        is_read_only: bool = False,
        resource_labels: dict = None,
    ) -> dict:
        """
        Update a policy.

        :param profile_id: ID of the profile.
        :param policy_id: ID of the policy.
        :param name: Name of the policy.
        :param access_type: Access type of the policy.
        :param condition: Condition of the policy.
        :param members: Dict of member type objects.
            Example: {
                users: [
                    {'id': '...'}
                ],
                tags: [
                    {'id': '...'}
                ],
                tokens: [
                    {'id': '...'}
                ],
                serviceIdentities: [
                    {'id': '...'}
                ],
            }
        :param is_active: Is active.
        :param is_draft: Is draft.
        :param is_read_only: Is read only.
        :param resource_labels: Resource labels.
            Example: {
                'additionalProp1': [
                    'string',
                ],
                ...
            }
        :return: Updated policy.
        """

        if members is None:
            members = []
        if resource_labels is None:
            resource_labels = {}

        params = {
            'name': name,
            'accessType': access_type,
            'condition': condition,
            'isActive': is_active,
            'isDraft': is_draft,
            'isReadOnly': is_read_only,
            'resourceLabels': resource_labels,
            'members': members,
        }

        return self.britive.patch(f'{self.base_url}/{profile_id}/policies/{policy_id}', json=params)

    def delete(self, profile_id: str, policy_id: str) -> None:
        """
        Delete a policy.

        :param profile_id: ID of the profile.
        :param policy_id: ID of the policy.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{profile_id}/policies/{policy_id}')
