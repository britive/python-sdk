class Policies:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/profiles'
    
    def list(self, profile_id):
        """
        Retrieve all policies for a profile.
        :param profile_id: ID of the profile.
        :return: List of policies.
        """
        return self.britive.get(f'{self.base_url}/{profile_id}/policies')

    def create(self, profile_id, name, access_type, description = "", condition = {}, is_active=True, is_draft = False, is_read_only = False, resource_label = {}, members = {}):
        """
        Create a new policy.
        :param profile_id: ID of the profile.
        :param name: Name of the policy.
        :param description: Description of the policy.
        :param access_type: Access type of the policy.
        :param condition: Condition of the policy.
        :param is_active: Is active.
        :param is_draft: Is draft.
        :param is_read_only: Is read only.
        :param resource_label: Resource label.
        :param members: Members. Valid values are users, tags, tokens, and serviceIdentities
        :return: Created policy.
        """
        params = {
            'name': name,
            'description': description,
            'accessType': access_type,
            'condition': condition,
            'isActive': is_active,
            'isDraft': is_draft,
            'isReadOnly': is_read_only,
            'resourceLabels': resource_label,
            'members': members
        }
        return self.britive.post(f'{self.base_url}/{profile_id}/policies', json=params)
    
    def get(self, profile_id, policy_id):
        """
        Retrieve a policy by ID.
        :param profile_id: ID of the profile.
        :param policy_id: ID of the policy.
        :return: Policy.
        """
        return self.britive.get(f'{self.base_url}/{profile_id}/policies/{policy_id}')
    
    def update(self, profile_id, policy_id, name, description, access_type, condition, members, is_active = True, is_draft = False, is_read_only = False, resource_label = {}):
        """
        Update a policy.
        :param profile_id: ID of the profile.
        :param policy_id: ID of the policy.
        :param name: Name of the policy.
        :param description: Description of the policy.
        :param access_type: Access type of the policy.
        :param condition: Condition of the policy.
        :param is_active: Is active.
        :param is_draft: Is draft.
        :param is_read_only: Is read only.
        :param resource_label: Resource label.
        :param members: Members. Valid values are users, tags, tokens, and serviceIdentities
        :return: Updated policy.
        """
        params = {
            'name': name,
            'description': description,
            'accessType': access_type,
            'condition': condition,
            'isActive': is_active,
            'isDraft': is_draft,
            'isReadOnly': is_read_only,
            'resourceLabels': resource_label,
            'members': members
        }
        return self.britive.patch(f'{self.base_url}/{profile_id}/policies/{policy_id}', json=params)
    
    def delete(self, profile_id, policy_id):
        """
        Delete a policy.
        :param profile_id: ID of the profile.
        :param policy_id: ID of the policy.
        :return: None
        """
        return self.britive.delete(f'{self.base_url}/{profile_id}/policies/{policy_id}')
    