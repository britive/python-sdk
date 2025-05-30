from .connection_metadata import ConnectionMetadata
from .connections import Connections
from .integrations import Integrations


class Itsm:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/itsm-manager'
        self.connection_metadata = ConnectionMetadata(britive)
        self.connections = Connections(britive)
        self.integrations = Integrations(britive)
