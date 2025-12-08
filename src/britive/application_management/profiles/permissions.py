class Permissions:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/paps'
        self.constraints = PermissionConstraints(britive)

    def add(self, profile_id: str, permission_type: str, permission_name: str) -> dict:
        """
        Add a permission to a profile.

        Call `list_available()` to see what permissions can be added.

        Note that for AWS and OCI permissions are not assigned to profiles as the permissions are tied into the
        cloud provider directly (AssumeRole for AWS).

        :param profile_id: The ID of the profile.
        :param permission_type: The type of permission. Valid values are `role`, `group`, and `policy`.
        :param permission_name: The name of the permission.
        :return: Details of the permission added.
        """

        data = {'op': 'add', 'permission': {'name': permission_name, 'type': permission_type}}

        return self.britive.post(f'{self.base_url}/{profile_id}/permissions', json=data)

    def list_assigned(self, profile_id: str, filter_expression: str = None) -> list:
        """
        List the permissions assigned to the profile.

        :param profile_id: The ID of the profile.
        :param filter_expression: Can filter based on `name`, `status`, `integrity check`. Valid operators are `eq` and
            `co`. Example: name co "Dev Account"
        :return: List of permissions assigned to the profile.
        """

        params = {'page': 0, 'size': 100}

        if filter_expression:
            params['filter'] = filter_expression

        return self.britive.get(f'{self.base_url}/{profile_id}/permissions', params=params)

    def list_available(self, profile_id: str) -> list:
        """
        List permissions available to be assigned to the profile.

        Note that for AWS and OCI permissions are not assigned to profiles as the permissions are tied into the
        cloud provider directly (AssumeRole for AWS).

        :param profile_id: The ID of the profile.
        :return: List of permissions that are available to be assigned to the profile.
        """

        params = {'page': 0, 'size': 100, 'query': 'available'}
        return self.britive.get(f'{self.base_url}/{profile_id}/permissions', params=params)

    def remove(self, profile_id: str, permission_type: str, permission_name: str) -> dict:
        """
        Remove a permission to a profile.

        :param profile_id: The ID of the profile.
        :param permission_type: The type of permission. Valid values are `role`, `group`, and `policy`.
        :param permission_name: The name of the permission.
        :return: Details of the permission removed.
        """

        data = {'op': 'remove', 'permission': {'name': permission_name, 'type': permission_type}}

        return self.britive.post(f'{self.base_url}/{profile_id}/permissions', json=data)


class PermissionConstraints:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/paps'

    def list_supported_types(self, profile_id: str, permission_name: str, permission_type: str = 'role') -> list:
        """
        Lists the supported constraint types.

        :param profile_id: The ID of the profile.
        :param permission_name: The name of the permission for which to list supported constraints.
        :param permission_type: The type of permission. Defaults to `role`.
        :returns: List of supported constraint types.
        """

        url = f'{self.base_url}/{profile_id}/permissions/{permission_name}/{permission_type}/supported-constraint-types'
        return self.britive.get(url)

    def get(self, profile_id: str, permission_name: str, constraint_type: str, permission_type: str = 'role') -> list:
        """
        Gets the list of constraints.

        :param profile_id: The ID of the profile.
        :param permission_name: The name of the permission for which to list supported constraints.
        :param constraint_type: The type of constraint.
        :param permission_type: The type of permission. Defaults to `role`.
        :returns: List of constraints for the given constraint type.
        """

        url = (
            f'{self.base_url}/{profile_id}/permissions/{permission_name}/'
            f'{permission_type}/constraints/{constraint_type}'
        )
        return self.britive.get(url).get('result')

    def lint_condition(
        self, profile_id: str, permission_name: str, expression: str, permission_type: str = 'role'
    ) -> dict:
        """
        Lint the provided condition expression.

        :param profile_id: The ID of the profile.
        :param permission_name: The name of the permission for which to lint the condition expression.
        :param expression: The condition expression to lint.
        :param permission_type: The type of permission. Defaults to `role`.
        :returns: Results of the lint operation.
        """

        url = f'{self.base_url}/{profile_id}/permissions/{permission_name}/{permission_type}/constraints/condition'

        params = {'operation': 'validate'}

        data = {'expression': expression}

        return self.britive.put(url, params=params, json=data)

    def add(
        self,
        profile_id: str,
        permission_name: str,
        constraint_type: str,
        constraint: dict,
        permission_type: str = 'role',
    ) -> None:
        """
        Adds the given constraint.

        :param profile_id: The ID of the profile.
        :param permission_name: The name of the permission for which the constraint should be added.
        :param constraint_type: The type of constraint.
        :param constraint: The constraint to add. If `constraint_type == 'condition'` then this parameter should be a
            dict with fields `title`, `description`, and `expression`. Otherwise, this parameter should be a dict with
            field `name` or string value.
        :param permission_type: The type of permission. Defaults to `role`.
        :returns: None.
        """

        url = (
            f'{self.base_url}/{profile_id}/permissions/{permission_name}/'
            f'{permission_type}/constraints/{constraint_type}'
        )

        params = {'operation': 'add'}

        return self.britive.put(url, params=params, json=constraint)

    def remove(
        self,
        profile_id: str,
        permission_name: str,
        constraint_type: str,
        constraint: dict = None,
        permission_type: str = 'role',
    ) -> None:
        """
        Removes the given constraint.

        :param profile_id: The ID of the profile.
        :param permission_name: The name of the permission for which the constraint should be removed.
        :param constraint_type: The type of constraint.
        :param constraint: The constraint to remove. If `constraint_type == 'condition'` then omit this parameter or
            set it to `None`. Otherwise, this parameter should be a dict with field `name` or string value.
        :param permission_type: The type of permission. Defaults to `role`.
        :returns: None.
        """

        url = (
            f'{self.base_url}/{profile_id}/permissions/{permission_name}/'
            f'{permission_type}/constraints/{constraint_type}'
        )
        params = {'operation': 'remove'}
        if constraint is None:
            constraint = {}

        return self.britive.put(url, params=params, json=constraint)
