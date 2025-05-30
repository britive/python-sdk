class Connections:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/itsm-manager/connections'

    def list(self) -> list:
        """
        Get a list of all ITSM connections.

        :return: A list of dictionaries containing details of all ITSM connections.
        """
        return self.britive.get(self.base_url)

    def create(
        self,
        connection_type: str,
        auth_type: str,
        name: str,
        description: str = '',
        data: dict = None,
    ) -> dict:
        """
        Create a new ITSM connection.

        :param connection_type: The type of ITSM connection.
        :param auth_type: The authentication type for the connection.
        :param name: The name of the connection.
        :param data: Additional connection authentication properties as a dictionary.
            Example:
                {
                    "apiToken": "...",
                    "loginUrl": "https://jira.atlassian.com",
                    "username": "first.last@example.com"
                }
        :param description: Optional. The description of the connection.
        :return: Details of the created ITSM connection.
        """

        payload = {
            'type': connection_type,
            'authType': auth_type,
            'name': name,
            'description': description,
            'data': data or {},
        }

        return self.britive.post(self.base_url, json=payload)

    def get(self, connection_id: str) -> dict:
        """
        Get details of a specific ITSM connection by ID.

        :param connection_id: The ID of the ITSM connection to retrieve.
        :return: A dictionary containing the details of the specified ITSM connection.
        """
        if not connection_id or not connection_id.strip():
            raise ValueError('connection_id must be a non-empty string')
        return self.britive.get(f'{self.base_url}/{connection_id}')

    def update(
        self,
        connection_id: str,
        connection_type: str = '',
        auth_type: str = '',
        name: str = '',
        description: str = '',
        data: dict = None,
    ) -> dict:
        """
        Update an existing ITSM connection.

        :param connection_id: The ID of the ITSM connection to update.
        :param connection_type: The type of ITSM connection.
        :param auth_type: The authentication type for the connection.
        :param name: The name of the connection.
        :param data: Additional connection authentication properties as a dictionary.
            Example:
                {
                    "apiToken": "...",
                    "loginUrl": "https://jira.atlassian.com",
                    "username": "first.last@example.com"
                }
        :param description: Optional. The description of the connection.
        :return: A dictionary containing the details of the updated ITSM connection.
        """

        payload = {}

        if connection_type:
            payload['type'] = connection_type
        if auth_type:
            payload['authType'] = auth_type
        if name:
            payload['name'] = name
        if description:
            payload['description'] = description
        if data:
            payload['data'] = data

        return self.britive.patch(f'{self.base_url}/{connection_id}', json=payload)

    def delete(self, connection_id: str) -> None:
        """
        Delete an ITSM connection by ID.

        :param connection_id: The ID of the ITSM connection to delete.
        :return: None.
        """
        if not connection_id or not connection_id.strip():
            raise ValueError('connection_id must be a non-empty string')
        self.britive.delete(f'{self.base_url}/{connection_id}')
