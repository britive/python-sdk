from .profiles.profiles import Profile
from .resources.resources import Resources
class AccessBroker:
    def __init__(self, britive):
        self.britive = britive
        self.profiles = Profile(britive)
        self.resources = Resources(britive)
        