
class SecurityPolicies:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/security-policies'

    def list(self) -> list:
        """
        Retrieve the list of all security policies in the system.

        :return: List of security policies.
        """

        return self.britive.get(self.base_url)

    def get(self, security_policy_id: str) -> dict:
        """
        Retrieve the details of the specified security policy.

        :param security_policy_id: The ID of the security policy.
        :return: Details of the security policy
        """

        return self.britive.get(f'{self.base_url}/{security_policy_id}')

    def create(self, name: str, effect: str, ips: list, tokens: list, description: str = None) -> dict:
        """
        Create a new security policy.

        Security policies are applied to API tokens and are currently only able to restrict usage to a set of IP
        addresses.

        :param name: Name of the security policy.
        :param effect: Valid values are `Allow` and `Deny`.
        :param ips: List of IP addresses in CIDR format (x.x.x.x/y). Individual IP addresses are also allowed.
        :param tokens: List of API token IDs for which this security policy should be applied.
        :param description: Optional description of the security policy.
        :return: Details of the newly created security policy.
        """

        data = {
            'name': name,
            'description': description or '',
            'effect': effect,
            'conditions': [
                {
                    'values': ips,
                    'type': 'ipAddress',
                    'evaluation': 'any'
                }
            ],
            'assignedTokens': [{'id': t} for t in tokens]
        }
        return self.britive.post(self.base_url, json=data)

    def enable(self, security_policy_id: str) -> None:
        """
        Enable a security policy.

        :param security_policy_id: The ID of the security policy.
        :return: None
        """

        return self.britive.patch(f'{self.base_url}/{security_policy_id}/enabled-statuses')

    def disable(self, security_policy_id: str) -> None:
        """
        Disable a security policy.

        :param security_policy_id: The ID of the security policy.
        :return: None
        """

        return self.britive.patch(f'{self.base_url}/{security_policy_id}/disabled-statuses')

    def update(self, security_policy_id: str, name: str = None, effect: str = None, ips: list = None,
               tokens: list = None, description: str = None) -> None:
        """
        Update a security policy.

        Only the parameters provided will be updated.

        :param security_policy_id: The ID of the security policy to update.
        :param name: Name of the security policy.
        :param effect: Valid values are `Allow` and `Deny`.
        :param ips: List of IP addresses in CIDR format (x.x.x.x/y). Individual IP addresses are also allowed.
        :param tokens: List of API token IDs for which this security policy should be applied.
        :param description: Optional description of the security policy.
        :return: Details of the newly created security policy.
        """

        # this update method is super strange - it doesn't following any of the standard update logic that other
        # resource types use.

        # first lets grab the existing security policy and then we can modify it based on what parameters have been
        # passed in.

        existing_policy = self.get(security_policy_id=security_policy_id)

        # construct part of the dict assuming every parameter is present
        raw_data = {
            'id': security_policy_id,
            'name': name,
            'description': description,
            'effect': effect
        }

        # and now remove any None values
        update = {k: v for k, v in raw_data.items() if v is not None}

        # handle the more complex attributes if needed
        if ips:
            update['conditions'] = [
                {
                    'values': ips,
                    'type': 'ipAddress',
                    'evaluation': 'any'
                }
            ]
        if tokens:
            update['assignedTokens'] = [{'id': t} for t in tokens]

        # and finally overwrite old values with new values, if they exist
        data = {**existing_policy, **update}
        
        return self.britive.put(f'{self.base_url}', json=data)

    def delete(self, security_policy_id: str) -> None:
        """
        Delete a security policy.

        :param security_policy_id: The ID of the security policy to update.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{security_policy_id}')
