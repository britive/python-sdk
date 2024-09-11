from .permissions import ResourcePermissions
from .types import ResourceTypes

class ResourceManager:

    def __init__(self, britive):
        self.britive = britive
        self.permissions = ResourcePermissions(britive)
        self.types = ResourceTypes(britive)