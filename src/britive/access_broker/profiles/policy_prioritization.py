class PolicyPrioritization:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/profiles'

    def enable(self, profile_id: str) -> None:
        """
        Enable policy prioritization for a profile.

        When enabled, policies will be evaluated in sequential order. Prioritizing policies may change
        existing access and/or approval conditions for affected identities.

        :param profile_id: ID of the profile.
        :return: None
        """

        return self.britive.patch(f'{self.base_url}/{profile_id}', json={'policyOrderingEnabled': True})

    def disable(self, profile_id: str) -> None:
        """
        Disable policy prioritization for a profile.

        When disabled, the system default policy processing will be used. This may change existing access
        and/or approval conditions for affected identities. Existing prioritization will be saved and may
        be restored later.

        :param profile_id: ID of the profile.
        :return: None
        """

        return self.britive.patch(f'{self.base_url}/{profile_id}', json={'policyOrderingEnabled': False})

    def reorder(self, profile_id: str, policy_ids: list) -> None:
        """
        Set the evaluation order of policies for a profile.

        Policy prioritization must be enabled for the profile before reordering.

        :param profile_id: ID of the profile.
        :param policy_ids: Ordered list of policy IDs. The first ID in the list will be evaluated first
            (order 0), the second will be order 1, and so on.
        :return: None
        """

        ordering = [{'id': policy_id, 'order': i} for i, policy_id in enumerate(policy_ids)]
        return self.britive.post(f'{self.base_url}/{profile_id}/policies/order', json=ordering)
