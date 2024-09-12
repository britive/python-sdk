from .permissions import ResourcePermissions
from .types import ResourceTypes
from .profile_manager import ProfileManager
from .labels import ResourceLabels
from .policy_manager import PolicyManager
class ResourceManager:

    def __init__(self, britive):
        self.britive = britive
        self.permissions = ResourcePermissions(britive)
        self.types = ResourceTypes(britive)
        self.profile_manager = ProfileManager(britive)
        self.labels = ResourceLabels(britive)
        self.policy_manager = PolicyManager(britive)
        