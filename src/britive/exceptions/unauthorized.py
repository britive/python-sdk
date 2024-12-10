from . import BritiveException


class BritiveUnauthorizedException(BritiveException):
    pass


class AuthenticationFailureError(BritiveUnauthorizedException):
    pass


class InvalidChallengeParameterError(BritiveUnauthorizedException):
    pass


class InvalidSsoProviderError(BritiveUnauthorizedException):
    pass


class UserNotFoundError(BritiveUnauthorizedException):
    pass


class UserDisabledError(BritiveUnauthorizedException):
    pass


class ServiceIdentityUserError(BritiveUnauthorizedException):
    pass


class UserValidationError(BritiveUnauthorizedException):
    pass


class InvalidOAuthTokenError(BritiveUnauthorizedException):
    pass


class SelfPasswordChangeError(BritiveUnauthorizedException):
    pass


class OtpValidationError(BritiveUnauthorizedException):
    pass


class UserMfaEnrollmentError(BritiveUnauthorizedException):
    pass


class AuthenticatedTempPasswordChangeError(BritiveUnauthorizedException):
    pass


class ForgottenPasswordError(BritiveUnauthorizedException):
    pass


class SsoLoginUserValidationError(BritiveUnauthorizedException):
    pass


class InvalidTenantError(BritiveUnauthorizedException):
    pass


class ApiTokenNotFoundError(BritiveUnauthorizedException):
    pass


class ApiTokenRevokedError(BritiveUnauthorizedException):
    pass


class ApiTokenExpiredError(BritiveUnauthorizedException):
    pass


class InvalidApiTokenError(BritiveUnauthorizedException):
    pass


class CliAuthenticationError(BritiveUnauthorizedException):
    pass


class InvalidCliTokenError(BritiveUnauthorizedException):
    pass


class AccountLockoutError(BritiveUnauthorizedException):
    pass


unauthorized_code_map = {
    # Error Codes for the Status Code 401 Unauthorized
    'AU-0000': AuthenticationFailureError,
    'AU-0001': InvalidChallengeParameterError,
    'AU-0002': InvalidSsoProviderError,
    'AU-0003': UserNotFoundError,
    'AU-0004': UserDisabledError,
    'AU-0005': ServiceIdentityUserError,
    'AU-0006': UserValidationError,
    'AU-0007': InvalidOAuthTokenError,
    'AU-0008': SelfPasswordChangeError,
    'AU-0009': OtpValidationError,
    'AU-0010': UserMfaEnrollmentError,
    'AU-0011': AuthenticatedTempPasswordChangeError,
    'AU-0012': ForgottenPasswordError,
    'AU-0013': SsoLoginUserValidationError,
    'AU-0014': InvalidTenantError,
    'AU-0015': ApiTokenNotFoundError,
    'AU-0016': ApiTokenRevokedError,
    'AU-0017': ApiTokenExpiredError,
    'AU-0018': InvalidApiTokenError,
    'AU-0019': CliAuthenticationError,
    'AU-0020': InvalidCliTokenError,
    'AU-0021': AccountLockoutError,
}
