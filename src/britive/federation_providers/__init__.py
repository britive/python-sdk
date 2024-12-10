from .aws import AwsFederationProvider
from .azure_system_assigned_managed_identity import AzureSystemAssignedManagedIdentityFederationProvider
from .azure_user_assigned_managed_identity import AzureUserAssignedManagedIdentityFederationProvider
from .bitbucket import BitbucketFederationProvider
from .federation_provider import FederationProvider
from .github import GithubFederationProvider
from .gitlab import GitlabFederationProvider
from .spacelift import SpaceliftFederationProvider


class FederationProviders:
    def __init__(self, britive) -> None:
        self.aws = AwsFederationProvider(britive)
        self.azure_system_assigned_managed_identity = AzureSystemAssignedManagedIdentityFederationProvider(britive)
        self.azure_user_assigned_managed_identity = AzureUserAssignedManagedIdentityFederationProvider(britive)
        self.bitbucket = BitbucketFederationProvider(britive)
        self.generic = FederationProvider(britive)
        self.github = GithubFederationProvider(britive)
        self.gitlab = GitlabFederationProvider(britive)
        self.spacelift = SpaceliftFederationProvider(britive)
