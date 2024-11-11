from .logs import Logs
from .webhooks import Webhooks


class AuditLogs:
    def __init__(self, britive) -> None:
        self.audit_logs = Logs(britive)
        self.audit_logs.webhooks = Webhooks(britive)
