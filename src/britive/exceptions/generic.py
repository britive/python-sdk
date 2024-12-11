from . import BritiveException


class BritiveGenericException(BritiveException):
    pass


class BritiveGenericError(BritiveGenericException):
    pass


class ValidationError(BritiveGenericException):
    pass


class DoesNotExistError(BritiveGenericException):
    pass


class DuplicateError(BritiveGenericException):
    pass


class UserInactiveError(BritiveGenericException):
    pass


class UserAssignedToProfileDirectlyError(BritiveGenericException):
    pass


class UserHasAccessViaTagError(BritiveGenericException):
    pass


class UserAccountLinkAlreadyExists(BritiveGenericException):
    pass


class ProfileWithMultipleConflictingTagsError(BritiveGenericException):
    pass


class UnsupportedFeatureError(BritiveGenericException):
    pass


class CannotUnmapManuallyAutomaticallyMappedAccounts(BritiveGenericException):
    pass


class InvalidEmailError(BritiveGenericException):
    pass


class EvaluationError(BritiveGenericException):
    pass


class ApprovalPendingError(BritiveGenericException):
    pass


class ApprovalRequiredError(BritiveGenericException):
    pass


class StepUpAuthenticationRequiredError(BritiveGenericException):
    pass


generic_code_map = {
    'E1000': BritiveGenericException,
    'E1001': BritiveGenericError,
    'E1003': ValidationError,
    'E1004': DoesNotExistError,
    'E1005': DuplicateError,
    'E1006': UserInactiveError,
    'E1008': UserAssignedToProfileDirectlyError,
    'E1009': UserHasAccessViaTagError,
    'E1010': UserAccountLinkAlreadyExists,
    'E1011': ProfileWithMultipleConflictingTagsError,
    'E1012': UnsupportedFeatureError,
    'E1013': CannotUnmapManuallyAutomaticallyMappedAccounts,
    'E1014': InvalidEmailError,
    'PE-0002': EvaluationError,
    'PE-0010': ApprovalPendingError,
    'PE-0011': ApprovalRequiredError,
    'PE-0028': StepUpAuthenticationRequiredError,
}
