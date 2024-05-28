class AccessDenied(Exception):
    pass


class ApiTokenNotFound(Exception):
    pass


class ApprovalRequiredButNoJustificationProvided(Exception):
    pass


class StepUpAuthRequiredButNotProvided(Exception):
    pass


class StepUpAuthFailed(Exception):
    pass


class StepUpAuthOTPNotProvided(Exception):
    pass


class ApprovalWorkflowRejected(Exception):
    pass


class ApprovalWorkflowTimedOut(Exception):
    pass


class ForbiddenRequest(Exception):
    pass


class InternalServerError(Exception):
    pass


class InvalidFederationProvider(Exception):
    pass


class InvalidRequest(Exception):
    pass


class MethodNotAllowed(Exception):
    pass


class NoSecretsVaultFound(Exception):
    pass


class NotExecutingInAzureEnvironment(Exception):
    pass


class NotExecutingInBitbucketEnvironment(Exception):
    pass


class NotExecutingInGithubEnvironment(Exception):
    pass


class NotExecutingInSpaceliftEnvironment(Exception):
    pass


class NotExecutingInGitlabEnvironment(Exception):
    pass


class NotFound(Exception):
    pass


class ProfileApprovalMaxBlockTimeExceeded(Exception):
    pass


class ProfileApprovalRejected(Exception):
    pass


class ProfileApprovalTimedOut(Exception):
    pass


class ProfileApprovalWithdrawn(Exception):
    pass


class ProfileCheckoutAlreadyApproved(Exception):
    pass


class ProfileNotFound(Exception):
    pass


class RootEnvironmentGroupNotFound(Exception):
    pass


class ServiceUnavailable(Exception):
    pass


class TenantMissingError(Exception):
    pass


class TokenMissingError(Exception):
    pass


class TooManyServiceIdentitiesFound(Exception):
    pass


class TooManyUsersFound(Exception):
    pass


class TransactionNotFound(Exception):
    pass


class UnauthorizedRequest(Exception):
    pass


class UserDoesNotHaveMFAEnabled(Exception):
    pass


class UserNotAllowedToChangePassword(Exception):
    pass


class UserNotAssociatedWithDefaultIdentityProvider(Exception):
    pass


class TenantUnderMaintenance(Exception):
    pass


# from https://docs.britive.com/docs/restapi-status-codes
allowed_exceptions = {
    400: InvalidRequest,
    401: UnauthorizedRequest,
    403: ForbiddenRequest,
    404: NotFound,
    405: MethodNotAllowed,
    500: InternalServerError,
    503: ServiceUnavailable,
}
