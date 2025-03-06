class ResponseTemplates:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/response-templates'

    def create(
        self,
        template_data: str,
        name: str,
        description: str = '',
        is_console_enabled: bool = False,
        show_on_ui: bool = False,
    ) -> dict:
        """
        Create a new response template.

        :param name: Name of the response template.
        :param description: Description of the response template.
        :param template_data: Template data.
        :param is_console_enabled: Is console enabled.
        :param show_on_ui: Show on UI.
        :return: Created response template.
        """

        params = {
            'name': name,
            'description': description,
            'template_data': template_data,
            'isConsoleAccessEnabled': is_console_enabled,
            'show_on_ui': show_on_ui,
        }

        return self.britive.post(self.base_url, json=params)

    def get(self, response_template_id: str) -> dict:
        """
        Retrieve a response template by ID.

        :param response_template_id: ID of the response template.
        :return: Response template.
        """

        return self.britive.get(f'{self.base_url}/{response_template_id}')

    def list(self, search_text: str = None) -> list:
        """
        Retrieve all response templates.

        :param search_text: filter by search text.
        :return: List of response templates.
        """

        params = {**({'searchText': search_text} if search_text else {})}

        return self.britive.get(self.base_url, params=params)['data']

    def update(
        self,
        response_template_id: str,
        name: str,
        description: str = None,
        template_data: str = None,
        is_console_enabled: bool = False,
    ) -> dict:
        """
        Update a response template.

        :param response_template_id: ID of the response template.
        :param name: Name of the response template.
        :param description: Description of the response template.
        :param template_data: Template data.
        :param is_console_enabled: Is console enabled.
        :return: Updated response template.
        """

        params = {'name': name}

        if description:
            params['description'] = description
        if template_data:
            params['template_data'] = template_data
        if is_console_enabled:
            params['is_console_enabled'] = is_console_enabled

        return self.britive.put(f'{self.base_url}/{response_template_id}', json=params)

    def delete(self, response_template_id: str) -> None:
        """
        Delete a response template.

        :param response_template_id: ID of the response template.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{response_template_id}')
