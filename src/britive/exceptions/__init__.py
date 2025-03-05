class BritiveException(Exception):
    pass


class AccessDenied(BritiveException):
    pass


class ApiTokenNotFound(BritiveException):
    pass


class ApprovalRequiredButNoJustificationProvided(BritiveException):
    pass


class ApprovalWorkflowRejected(BritiveException):
    pass


class ApprovalWorkflowTimedOut(BritiveException):
    pass


class Conflict(BritiveException):
    pass


class ForbiddenRequest(BritiveException):
    pass


class InternalServerError(BritiveException):
    pass


class InvalidFederationProvider(BritiveException):
    pass


class InvalidRequest(BritiveException):
    pass


class MethodNotAllowed(BritiveException):
    pass


class MissingAzureDependency(BritiveException):
    pass


class NoSecretsVaultFound(BritiveException):
    pass


class NotExecutingInAzureEnvironment(BritiveException):
    pass


class NotExecutingInBitbucketEnvironment(BritiveException):
    pass


class NotExecutingInGithubEnvironment(BritiveException):
    pass


class NotExecutingInSpaceliftEnvironment(BritiveException):
    pass


class NotExecutingInGitlabEnvironment(BritiveException):
    pass


class NotFound(BritiveException):
    pass


class ProfileApprovalMaxBlockTimeExceeded(BritiveException):
    pass


class ProfileApprovalRejected(BritiveException):
    pass


class ProfileApprovalTimedOut(BritiveException):
    pass


class ProfileApprovalWithdrawn(BritiveException):
    pass


class ProfileCheckoutAlreadyApproved(BritiveException):
    pass


class ProfileNotFound(BritiveException):
    pass


class RootEnvironmentGroupNotFound(BritiveException):
    pass


class ServiceUnavailable(BritiveException):
    pass


class StepUpAuthFailed(BritiveException):
    pass


class StepUpAuthOTPNotProvided(BritiveException):
    pass


class StepUpAuthRequiredButNotProvided(BritiveException):
    pass


class TenantMissingError(BritiveException):
    pass


class TenantUnderMaintenance(BritiveException):
    pass


class TokenMissingError(BritiveException):
    pass


class TooManyServiceIdentitiesFound(BritiveException):
    pass


class TooManyUsersFound(BritiveException):
    pass


class TransactionNotFound(BritiveException):
    pass


class UnauthorizedRequest(BritiveException):
    pass


class UserDoesNotHaveMFAEnabled(BritiveException):
    pass


class UserNotAllowedToChangePassword(BritiveException):
    pass


class UserNotAssociatedWithDefaultIdentityProvider(BritiveException):
    pass


# from https://docs.britive.com/docs/restapi-status-codes
allowed_exceptions = {
    400: InvalidRequest,
    401: UnauthorizedRequest,
    403: ForbiddenRequest,
    404: NotFound,
    405: MethodNotAllowed,
    409: Conflict,
    500: InternalServerError,
    503: ServiceUnavailable,
}
