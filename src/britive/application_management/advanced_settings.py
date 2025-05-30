class AdvancedSettings:
    def __init__(self, britive, base_url: str = '/apps/{}/advanced-settings') -> None:
        self.britive = britive
        self.base_url = self.britive.base_url + base_url

    def create(self, entity_id: str, settings: dict) -> dict:
        """
        Create Advanced Settings for a specific application or profile.

        :param entity_id: The ID of the application or profile to create Advanced Settings for.
        :param settings: The Advanced Settings settings.
        :return: Details of the created Advanced Settings.
        """

        return self.britive.post(self.base_url.format(entity_id), json=settings)

    def get(self, entity_id: str) -> dict:
        """
        Get Advanced Settings for a specific application or profile.

        :param entity_id: The ID of the application or profile to retrieve Advanced Settings for.
        :return: Details of the Advanced Settings.
        """

        return self.britive.get(self.base_url.format(entity_id))

    def update(self, entity_id: str, settings: dict) -> dict:
        """
        Update Advanced Settings for a specific application or profile.

        :param entity_id: The ID of the application or profile to update Advanced Settings for.
        :param settings: The Advanced Settings settings to update.
        :return: Details of the updated Advanced Settings.
        """

        return self.britive.put(self.base_url.format(entity_id), json=settings)

    def delete(self, entity_id: str, settings_id: str) -> None:
        """
        Delete Advanced Settings for a specific application or profile.

        :param entity_id: The ID of the application or profile associated with the Advanced Settings.
        :param settings_id: The ID of the Advanced Settings settings to delete.
        :return: None.
        """

        self.britive.delete(f'{self.base_url.format(entity_id)}/{settings_id}')
