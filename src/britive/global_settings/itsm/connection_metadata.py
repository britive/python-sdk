from typing import Union


class ConnectionMetadata:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/itsm-manager/connection-templates'

    def list(self) -> list[str]:
        """
        Get a list of supported ITSM connection types.

        :return: A list of supported ITSM connection type identifiers.
        """

        return self.britive.get(f'{self.base_url}/supported-types')

    def get(self, connection_type: str = '') -> Union[list, dict]:
        """
        Get ITSM connection metadata details for all supported types or a specific type.

        :param template_type: Optional. The ITSM connection type to retrieve metadata for (e.g., 'servicenow').
            If empty or not provided, returns metadata for all supported types.
        :return: Details of ITSM connection metadata for all supported types or a specific type.
        """

        return self.britive.get(f'{self.base_url}/{connection_type}'.rstrip('/'))
