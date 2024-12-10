from .api_tokens import ApiTokens
from .policies import SecurityPolicies
from .saml import Saml
from .step_up import StepUpAuth


class Security:
    def __init__(self, britive) -> None:
        self.api_tokens = ApiTokens(britive)
        self.saml = Saml(britive)
        self.security_policies = SecurityPolicies(britive)
        self.step_up_auth = StepUpAuth(britive)
