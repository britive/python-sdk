from .permissions import ResourcePermissions
from .types import ResourceTypes
from .profile_manager import ProfileManager
from .labels import ResourceLabels
class ResourceManager:

    def __init__(self, britive):
        self.britive = britive
        self.permissions = ResourcePermissions(britive)
        self.types = ResourceTypes(britive)
        self.profile_manager = ProfileManager(britive)
        self.labels = ResourceLabels(britive)
        