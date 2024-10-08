from .profiles.profiles import Profile
from .resources.resources import Resources
from .response_templates import ResponseTemplates


class AccessBroker:
    def __init__(self, britive):
        self.britive = britive
        self.profiles = Profile(britive)
        self.resources = Resources(britive)
        self.response_templates = ResponseTemplates(britive)
