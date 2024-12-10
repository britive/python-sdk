from .logs import Logs
from .webhooks import Webhooks


class AuditLogs:
    def __init__(self, britive) -> None:
        self.logs = Logs(britive)
        self.webhooks = Webhooks(britive)
