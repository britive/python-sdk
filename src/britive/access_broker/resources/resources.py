from .labels import Labels
from .types import Types
from .permissions import Permissions
class Resources:
    def __init__(self, britive):
        self.britive = britive
        self.labels = Labels(britive)
        self.types = Types(britive)
        self.permissions = Permissions(britive)
        
