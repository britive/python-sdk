class Labels:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/labels'

    def create(self, name: str, description: str = '', values: list = None) -> dict:
        """
        Create a new label.

        :param name: Name of the label.
        :param description: Description of the label.
        :param values: List of values. Format [{'key': 'value'}, ...]
        :return: Created label.
        """

        if values is None:
            values = []

        params = {'keyName': name, 'description': description, 'values': values}

        return self.britive.post(self.base_url, json=params)

    def get(self, label_id: str) -> dict:
        """
        Retrieve a label by ID.

        :param label_id: ID of the label.
        :return: Label.
        """

        return self.britive.get(f'{self.base_url}/{label_id}')

    def list(self) -> list:
        """
        Retrieve all labels.

        :return: List of labels.
        """
        return self.britive.get(self.base_url)

    def update(self, label_id: str, name: str = None, description: str = None, values: list = None) -> dict:
        """
        Update a label.

        :param label_id: ID of the label.
        :param name: Name of the label.
        :param description: Description of the label.
        :param values: List of values. Format [{'key': 'value'}, ...]
        :return: Updated label.
        """

        params = {}

        if name:
            params['keyName'] = name
        if description:
            params['description'] = description
        if values:
            params['values'] = values

        return self.britive.put(f'{self.base_url}/{label_id}', json=params)

    def delete(self, label_id: str) -> None:
        """
        Delete a label.

        :param label_id: ID of the label.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{label_id}')
