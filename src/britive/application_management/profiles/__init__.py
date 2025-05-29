from britive import exceptions
from britive.application_management.advanced_settings import AdvancedSettings

from .additional_settings import AdditionalSettings
from .permissions import Permissions
from .policies import Policies
from .session_attributes import SessionAttributes

creation_defaults = {
    'expirationDuration': 3600000,
    'extensionDuration': 1800000,
    'notificationPriorToExpiration': 300000,
    'extendable': False,
    'extensionLimit': '1',
    'status': 'active',
    'destinationUrl': '',
    'useDefaultAppUrl': True,
    'description': '',
}

update_fields_to_keep: list = list(creation_defaults)
update_fields_to_keep.append('name')
update_fields_to_keep.remove('status')


class Profiles:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/apps'
        self.additional_settings = AdditionalSettings(britive)
        self.advanced_settings = AdvancedSettings(britive, base_url='/paps/{}/advanced-settings')
        self.permissions = Permissions(britive)
        self.policies = Policies(britive)
        self.session_attributes = SessionAttributes(britive)

    def create(self, application_id: str, name: str, **kwargs) -> dict:
        """
        Create a profile.

        :param application_id: The ID of the application under which the profile will be created.
        :param name: The name of the profile. This is the only required argument.
        :param kwargs: A key/value mapping consisting of the following fields. If any/all are omitted default values
            will be used. The keys and default values are provided below.

            - expirationDuration: 3600000
            - extensionDuration: 1800000
            - notificationPriorToExpiration: 300000
            - extendable: False
            - extensionLimit: '1'
            - status: 'active'
            - destinationUrl: ''
            - useDefaultAppUrl: True
            - description: ''
            - scope: if not provided, no scopes will be applied. If provided it must follow the
                format listed below.

                [
                    {
                        'type': 'EnvironmentGroup'|'Environment',
                        'value':'ID'
                    },
                ]

        :return: Details of the newly created profile.
        """

        kwargs['appContainerId'] = application_id
        kwargs['name'] = name  # required field, so it is being called out explicitly in the method parameters

        # merge defaults and provided information - keys in kwargs will overwrite the defaults in creation_defaults
        data = {**creation_defaults, **kwargs}  # note python 3.5 or greater but only 3.5 and up are supported so okay!

        return self.britive.post(f'{self.base_url}/{application_id}/paps', json=data)

    def list(
        self,
        application_id: str,
        filter_expression: str = None,
        environment_association: str = None,
        include_policies: bool = False,
    ) -> list:
        """
        Return an optionally filtered list of profiles associated with the specified application.

        :param application_id: The ID of the application.
        :param filter_expression: Can filter based on `name`, `status`, `integrity check`. Valid operators are `eq` and
            `co`. Example: name co "Dev Account"
        :param environment_association: Only list profiles with associations to the specified environment. Cannot be
            used in conjunction with `filter_expression`. Example: `environment_association="109876543210"`
        :param include_policies: Defaults to False. If set to True will include all policies on each profile and all
            members on each policy. Cannot be used in conjunction with `filter_expression`.
        :return: List of profiles.
        """

        if filter_expression and environment_association:
            raise exceptions.InvalidRequest(
                'Cannot specify `filter_expression` and `environment_association` in the same request.'
            )

        params = {
            'page': 0,
            'size': 100,
            'view': 'summary',  # this is required - omitting it results in a 400 not authorized error
        }

        if include_policies:
            params['view'] = 'includePolicies'

        if filter_expression:
            params['filter'] = filter_expression

        if environment_association:
            params['environment'] = environment_association

        return self.britive.get(f'{self.base_url}/{application_id}/paps', params=params)

    def get(self, application_id: str, profile_id: str, summary: bool = None) -> dict:
        """
        Return details of the provided profile.

        :param application_id: The ID of the application.
        :param profile_id: The ID of the profile.
        :param summary: Whether to provide a summarized response. Defaults to None to support backwards compatibility
            with the legacy functionality/way of obtaining details of the profile. Setting to True will return a
            summarized set of attributes for the profile. Setting to False will return a larger set of attributes
            for the profile.
        :return: Details of the profile.
        :raises: ProfileNotFound if the profile does not exist.
        """

        if summary is None:
            for profile in self.list(application_id=application_id):
                if profile['papId'] == profile_id:
                    return profile
            raise exceptions.ProfileNotFound
        params = {}
        if summary:
            params['view'] = 'summary'
        return self.britive.get(f'{self.britive.base_url}/paps/{profile_id}', params=params)

    def update(self, application_id: str, profile_id: str, **kwargs) -> dict:
        """
        Update details of the specified profile.

        :param application_id: The ID of the application.
        :param profile_id: The ID of the profile to update.
        :param kwargs: Refer to the `create()` method for details on parameters that can be provided. For this update
            action no default values will be injected for missing parameters.
        :return: Details of the updated profile.
        """

        existing = self.get(application_id=application_id, profile_id=profile_id, summary=True)
        base = {key: existing[key] for key in update_fields_to_keep}

        kwargs['appContainerId'] = application_id
        data = {**base, **kwargs}

        return self.britive.patch(f'{self.base_url}/{application_id}/paps/{profile_id}', json=data)

    def available_resources(self, profile_id: str, filter_expression: str = None) -> list:
        """
        AZURE ONLY. This API is applicable to Azure applications only.

        Returns the list of all resource scopes that are available and can be added to a profile.

        :param profile_id: The ID of the profile.
        :param filter_expression: Can filter based on `name`, `status`, `integrity check`. Valid operators are `eq` and
            `co`. Example: name co "Dev Account"
        :return: List of available resource scopes.
        """

        params = {'page': 0, 'size': 100}

        if filter_expression:
            params['filter'] = filter_expression

        return self.britive.get(f'{self.britive.base_url}/paps/{profile_id}/resources', params=params)

    def get_scopes(self, profile_id: str) -> list:
        """
        Get the scopes associated with the specified profile.

        :param profile_id: The ID of the profile for which scopes will be updated.
        :return: List of scopes and associated details.
        """

        return self.britive.get(f'{self.britive.base_url}/paps/{profile_id}/scopes')

    def set_scopes(self, profile_id: str, scopes: list) -> list:
        """
        Update the scopes associated with the specified profile.

        :param profile_id: The ID of the profile for which scopes will be updated.
        :param scopes: List of scopes. Example  below.
            [
                {
                    'type': 'EnvironmentGroup'|'Environment',
                    'value':'ID'
                },
            ]
        :return: List of scopes and associated details.
        """

        return self.britive.post(f'{self.britive.base_url}/paps/{profile_id}/scopes', json=scopes)

    def add_single_environment_scope(self, profile_id: str, environment_id: str) -> None:
        """
        Add a single environment to the scopes associated with the specified profile.

        This API call is useful when there are a large number of environments (500+) as the
        `set_scopes()` call may time out.

        :param profile_id: The ID of the profile.
        :param environment_id: The ID of the environment which will be added to the profile scopes.
        :return: None
        """

        return self.britive.patch(f'{self.britive.base_url}/paps/{profile_id}/scopes/{environment_id}')

    def remove_single_environment_scope(self, profile_id: str, environment_id: str) -> None:
        """
        Remove a single environment from the scopes associated with the specified profile.

        This API call is useful when there are a large number of environments (500+) as the
        `set_scopes()` call may time out.

        :param profile_id: The ID of the profile.
        :param environment_id: The ID of the environment which will be removed from the profile scopes.
        :return: None
        """

        return self.britive.delete(f'{self.britive.base_url}/paps/{profile_id}/scopes/{environment_id}')

    def enable(self, application_id: str, profile_id: str) -> dict:
        """
        Enables a profile.

        :param application_id: The ID of the application.
        :param profile_id: The ID of the profile to enable.
        :return: Details of the enabled profile.
        """

        return self.britive.post(f'{self.base_url}/{application_id}/paps/{profile_id}/enabled-statuses')

    def disable(self, application_id: str, profile_id: str) -> dict:
        """
        Disables a profile.

        :param application_id: The ID of the application.
        :param profile_id: The ID of the profile to disable.
        :return: Details of the disabled profile.
        """

        return self.britive.post(f'{self.base_url}/{application_id}/paps/{profile_id}/disabled-statuses')

    def delete(self, application_id: str, profile_id: str) -> None:
        """
        Deletes a profile.

        :param application_id: The ID of the application.
        :param profile_id: The ID of the profile to delete.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{application_id}/paps/{profile_id}')
