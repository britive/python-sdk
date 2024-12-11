from .identity_attributes import IdentityAttributes
from .identity_providers import IdentityProviders
from .service_identities import ServiceIdentities, ServiceIdentityTokens
from .tags import Tags
from .users import Users
from .workload import Workload


class IdentityManagement:
    def __init__(self, britive) -> None:
        self.identity_attributes = IdentityAttributes(britive)
        self.identity_providers = IdentityProviders(britive)
        self.service_identities = ServiceIdentities(britive)
        self.service_identity_tokens = ServiceIdentityTokens(britive)
        self.tags = Tags(britive)
        self.users = Users(britive)
        self.workload = Workload(britive)
