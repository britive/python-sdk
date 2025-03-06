from .brokers import Brokers
from .pools import Pools
from .profiles import Profiles
from .resources import Resources
from .response_templates import ResponseTemplates


class AccessBroker:
    def __init__(self, britive) -> None:
        self.brokers = Brokers(britive)
        self.pools = Pools(britive)
        self.profiles = Profiles(britive)
        self.resources = Resources(britive)
        self.response_templates = ResponseTemplates(britive)
