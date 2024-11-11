from .actions import SystemActions
from .consumers import SystemConsumers
from .permissions import SystemPermissions
from .policies import SystemPolicies
from .roles import SystemRoles


class System:
    def __init__(self, britive) -> None:
        self.roles = SystemRoles(britive)
        self.policies = SystemPolicies(britive)
        self.permissions = SystemPermissions(britive)
        self.consumers = SystemConsumers(britive)
        self.actions = SystemActions(britive)
