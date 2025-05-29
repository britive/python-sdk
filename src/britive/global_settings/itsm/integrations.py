class Integrations:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/itsm-integration'

    def validate_filter(
        self,
        connection_id: str,
        filters: dict = None,
        ticket_id: str = '',
        ticket_type: str = '',
        variables: dict = None,
    ) -> dict:
        """
        Validate the filter criteria and ticket for the ITSM integration settings.

        :param connection_id: The ID of the ITSM connection to validate against.
        :param ticket_type: Optional. The type of ITSM ticket.
        :param filters: Optional. Additional filter properties.
        :param ticket_id: Optional. ITSM ticket ID.
        :param ticket_type: Optional. ITSM ticket type.
        :param variables: Optional. Additional filter variables.
        :return: Filter validation result.
        """

        payload = {'connectionId': connection_id}
        if filters:
            payload['filter'] = filters
        if ticket_id:
            payload['ticketId'] = ticket_id
        if ticket_type:
            payload['ticketType'] = ticket_type
        if variables:
            payload['variableMap'] = variables

        return self.britive.post(f'{self.base_url}/filter-validation', json=payload)

    def get_ticket(self, connection_id: str, ticket_id: str, ticket_type: str) -> None:
        """
        Get the ticket details.

        :param connection_id: The ID of the ITSM connection.
        :param ticket_id: ITSM ticket ID.
        :param ticket_type: ITSM ticket type.
        :return: Details of the ticket.
        """

        self.britive.get(f'{self.base_url}/connections/{connection_id}/ticketTypes/{ticket_type}/tickets/{ticket_id}')
