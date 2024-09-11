from .resource_permissions import ResourcePermissions
from .resource_types import ResourceTypes

class ResourceManager:

    def __init__(self, britive):
        self.britive = britive
        self.resource_permissions = ResourcePermissions(britive)
        self.resource_types = ResourceTypes(britive)