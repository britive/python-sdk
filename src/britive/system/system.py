from .roles import SystemRoles
from .policies import SystemPolicies
from .permissions import SystemPermissions
from .consumers import SystemConsumers
from .actions import SystemActions


# this class is just a logical grouping construct


class System:
    def __init__(self, britive):
        self.britive = britive
        self.roles = SystemRoles(britive)
        self.policies = SystemPolicies(britive)
        self.permissions = SystemPermissions(britive)
        self.consumers = SystemConsumers(britive)
        self.actions = SystemActions(britive)

