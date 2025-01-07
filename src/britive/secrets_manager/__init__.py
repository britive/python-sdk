from .folders import Folders
from .policies import PasswordPolicies, Policies
from .resources import Resources
from .secrets import Secrets
from .templates import StaticSecretTemplates
from .vaults import Vaults


class SecretsManager:
    def __init__(self, britive) -> None:
        self.vaults = Vaults(britive)
        self.password_policies = PasswordPolicies(britive)
        self.secrets = Secrets(britive)
        self.policies = Policies(britive)
        self.static_secret_templates = StaticSecretTemplates(britive)
        self.resources = Resources(britive)
        self.folders = Folders(britive)
