
class TenantMissingError(Exception):
    pass


class TokenMissingError(Exception):
    pass


class TooManyUsersFound(Exception):
    pass


class TooManyServiceIdentitiesFound(Exception):
    pass


class InvalidRequest(Exception):
    pass


class UnauthorizedRequest(Exception):
    pass


class ForbiddenRequest(Exception):
    pass


class MethodNotAllowed(Exception):
    pass


class InternalServerError(Exception):
    pass


class ServiceUnavailable(Exception):
    pass


class UserDoesNotHaveMFAEnabled(Exception):
    pass


class UserNotAllowedToChangePassword(Exception):
    pass


class UserNotAssociatedWithDefaultIdentityProvider(Exception):
    pass


class ProfileNotFound(Exception):
    pass


class RootEnvironmentGroupNotFound(Exception):
    pass


class ApiTokenNotFound(Exception):
    pass


class TransactionNotFound(Exception):
    pass


class ApprovalRequiredButNoJustificationProvided(Exception):
    pass


class ApprovalWorkflowTimedOut(Exception):
    pass


class ApprovalWorkflowRejected(Exception):
    pass


class AccessDenied(Exception):
    pass


class TenantNotEnabledForProfilesVersion1(Exception):
    pass


class TenantNotEnabledForProfilesVersion2(Exception):
    pass


class ProfileApprovalTimedOut(Exception):
    pass


class ProfileApprovalRejected(Exception):
    pass


class ProfileApprovalWithdrawn(Exception):
    pass


class ProfileApprovalMaxBlockTimeExceeded(Exception):
    pass


class NoSecretsVaultFound(Exception):
    pass


class InvalidFederationProvider(Exception):
    pass


class NotExecutingInGithubEnvironment(Exception):
    pass


class NotExecutingInBitbucketEnvironment(Exception):
    pass


class NotExecutingInAzureEnvironment(Exception):
    pass


# from https://docs.britive.com/docs/restapi-status-codes
allowed_exceptions = {
    400: InvalidRequest,
    401: UnauthorizedRequest,
    403: ForbiddenRequest,
    405: MethodNotAllowed,
    500: InternalServerError,
    503: ServiceUnavailable
}