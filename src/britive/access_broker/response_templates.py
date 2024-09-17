class ResponseTemplates:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/response-templates'
    
    def create(self, name, description = "", template_data = "", is_console_enabled = False, created_by = "", updated_by = ""):
        """
        Create a new response template.
        :param name: Name of the response template.
        :param description: Description of the response template.
        :param template_data: Template data.
        :param is_console_enabled: Is console enabled.
        :param created_by: Created by.
        :param updated_by: Updated by.
        :return: Created response template.
        """
        params = {
            'name': name,
            'description': description,
            'templateData': template_data,
            'isConsoleEnabled': is_console_enabled,
            'createdBy': created_by,
            'updatedBy': updated_by
        }
        return self.britive.post(self.base_url, json=params)
    
    def list(self):
        """
        Retrieve all response templates.
        :return: List of response templates.
        """
        return self.britive.get(self.base_url)
    
    def update(self, response_template_id, name = "", description = "", template_data = "", is_console_enabled = False, created_by = "", updated_by = ""):
        """
        Update a response template.
        :param response_template_id: ID of the response template.
        :param name: Name of the response template.
        :param description: Description of the response template.
        :param template_data: Template data.
        :param is_console_enabled: Is console enabled.
        :param created_by: Created by.
        :param updated_by: Updated by.
        :return: Updated response template.
        """
        params = {
            'name': name,
            'description': description,
            'templateData': template_data,
            'isConsoleEnabled': is_console_enabled,
            'createdBy': created_by,
            'updatedBy': updated_by
        }
        return self.britive.put(f'{self.base_url}/{response_template_id}', json=params)
    
    def get(self, response_template_id):
        """
        Retrieve a response template by ID.
        :param response_template_id: ID of the response template.
        :return: Response template.
        """
        return self.britive.get(f'{self.base_url}/{response_template_id}')
    
    def delete(self, response_template_id):
        """
        Delete a response template.
        :param response_template_id: ID of the response template.
        :return: None
        """
        return self.britive.delete(f'{self.base_url}/{response_template_id}')