class HelperMethods:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/access'

    def get_profile_and_environment_ids_given_names(
        self, profile_name: str, environment_name: str, application_name: str = None
    ) -> dict:
        ids = None
        environment_found = False
        profile_found = False
        for app in self.britive.get(self.base_url):
            if application_name and app['appName'].lower() != application_name.lower():
                continue
            if not (
                profile := next((p for p in app['profiles'] if p['profileName'].lower() == profile_name.lower()), None)
            ):
                continue
            profile_found = True
            if environment := next(
                (e for e in profile['environments'] if e['environmentName'].lower() == environment_name.lower()), None
            ):
                environment_found = True
                if ids:
                    raise ValueError(
                        f'multiple combinations of profile `{profile_name}` and environment '
                        f'`{environment_name}` exist so no unique combination can be determined. Please '
                        f'provide the optional parameter `application_name` to clarify which application '
                        f'the environment belongs to.'
                    )
                ids = {'profile_id': profile['profileId'], 'environment_id': environment['environmentId']}
        if not profile_found:
            raise ValueError(f'profile `{profile_name}` not found.')
        if profile_found and not environment_found:
            raise ValueError(f'profile `{profile_name}` found but not in environment `{environment_name}`.')
        return ids

    def get_profile_and_resource_ids_given_names(self, profile_name: str, resource_name: str) -> dict:
        resource_profile_map = {
            f'{item["resourceName"].lower()}|{item["profileName"].lower()}': {
                'profile_id': item['profileId'],
                'resource_id': item['resourceId'],
            }
            for item in self.britive.get(f'{self.britive.base_url}/resource-manager/my-resources')
        }

        item = resource_profile_map.get(f'{resource_name.lower()}|{profile_name.lower()}')

        # do some error checking
        if not item:
            raise ValueError('resource and profile combination not found')

        return item
