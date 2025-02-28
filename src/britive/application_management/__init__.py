from .access_builder import AccessBuilderSettings
from .accounts import Accounts
from .applications import Applications
from .environment_groups import EnvironmentGroups
from .environments import Environments
from .groups import Groups
from .managed_permissions import ManagedPermissions
from .permissions import Permissions
from .profiles import Profiles
from .scans import Scans


class ApplicationManagement:
    def __init__(self, britive) -> None:
        self.access_builder = AccessBuilderSettings(britive)
        self.accounts = Accounts(britive)
        self.applications = Applications(britive)
        self.environment_groups = EnvironmentGroups(britive)
        self.environments = Environments(britive)
        self.groups = Groups(britive)
        self.managed_permissions = ManagedPermissions(britive)
        self.permissions = Permissions(britive)
        self.profiles = Profiles(britive)
        self.scans = Scans(britive)
