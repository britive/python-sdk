from . import BritiveException


class BritiveBadRequestException(BritiveException):
    pass


class ApplicationCreationError(BritiveBadRequestException):
    pass


class ApplicationPropertiesReadError(BritiveBadRequestException):
    pass


class ApplicationUpdateError(BritiveBadRequestException):
    pass


class ApplicationDeletionError(BritiveBadRequestException):
    pass


class ApplicationSavePropertiesError(BritiveBadRequestException):
    pass


class MissingJustificationError(BritiveBadRequestException):
    pass


class InvalidJustificationError(BritiveBadRequestException):
    pass


class MissingTicketError(BritiveBadRequestException):
    pass


class MissingTicketTypeError(BritiveBadRequestException):
    pass


class MissingTicketIdError(BritiveBadRequestException):
    pass


class InvalidTicketTypeError(BritiveBadRequestException):
    pass


class InvalidTicketIdError(BritiveBadRequestException):
    pass


class ApiTokenCreationError(BritiveBadRequestException):
    pass


class ApiTokenUpdateError(BritiveBadRequestException):
    pass


class ApiTokenDeletionError(BritiveBadRequestException):
    pass


class AwsProfileCheckInError(BritiveBadRequestException):
    pass


class AzureProfileCheckInError(BritiveBadRequestException):
    pass


class GcpProfileCheckInError(BritiveBadRequestException):
    pass


class OracleProfileCheckInError(BritiveBadRequestException):
    pass


class SalesForceProfileCheckInError(BritiveBadRequestException):
    pass


class ServiceNowProfileCheckInError(BritiveBadRequestException):
    pass


class OktaProfileCheckInError(BritiveBadRequestException):
    pass


class SnowflakeProfileCheckInError(BritiveBadRequestException):
    pass


class BritiveProfileCheckInError(BritiveBadRequestException):
    pass


class AwsIdentityCenterProfileCheckInError(BritiveBadRequestException):
    pass


class AwsProfileCheckOutError(BritiveBadRequestException):
    pass


class AzureProfileCheckOutError(BritiveBadRequestException):
    pass


class GcpProfileCheckOutError(BritiveBadRequestException):
    pass


class OracleProfileCheckOutError(BritiveBadRequestException):
    pass


class SalesForceProfileCheckOutError(BritiveBadRequestException):
    pass


class ServiceNowProfileCheckOutError(BritiveBadRequestException):
    pass


class OktaProfileCheckOutError(BritiveBadRequestException):
    pass


class SnowflakeProfileCheckOutError(BritiveBadRequestException):
    pass


class BritiveProfileCheckOutError(BritiveBadRequestException):
    pass


class AwsIdentityCenterProfileCheckOutError(BritiveBadRequestException):
    pass


class ProfileCheckInError(BritiveBadRequestException):
    pass


class ProfileCheckOutError(BritiveBadRequestException):
    pass


class ProfileStatusReadError(BritiveBadRequestException):
    pass


class ProfileStatusUpdateError(BritiveBadRequestException):
    pass


class ProfileSharedAccountsReadError(BritiveBadRequestException):
    pass


class ProfileSnapshotDeletionError(BritiveBadRequestException):
    pass


class ProfileSnapshotCreationError(BritiveBadRequestException):
    pass


class ProfileAlreadyCheckedInError(BritiveBadRequestException):
    pass


class ApprovalJustificationRequiredError(BritiveBadRequestException):
    pass


class ProfileApprovalRequiredError(BritiveBadRequestException):
    pass


class PendingProfileApprovalRequestError(BritiveBadRequestException):
    pass


class ProfileCreationError(BritiveBadRequestException):
    pass


class ProfileReadError(BritiveBadRequestException):
    pass


class ProfileUpdateError(BritiveBadRequestException):
    pass


class ProfileDeletionError(BritiveBadRequestException):
    pass


class ProfileValidationError(BritiveBadRequestException):
    pass


class ProfileFavoriteSaveError(BritiveBadRequestException):
    pass


class ProfileFavoriteDeleteError(BritiveBadRequestException):
    pass


class ProfileFavoriteReadError(BritiveBadRequestException):
    pass


class ProfileRequestError(BritiveBadRequestException):
    pass


class ProfilePolicyPermissionsError(BritiveBadRequestException):
    pass


class ProfilePolicyInvalidTokenError(BritiveBadRequestException):
    pass


class ProfilePolicyCreationError(BritiveBadRequestException):
    pass


class ProfilePolicyUpdateError(BritiveBadRequestException):
    pass


class ProfilePolicyGenericError(BritiveBadRequestException):
    pass


class ProfilePolicyCreationUpdateError(BritiveBadRequestException):
    pass


class ResourceFavoriteRemovalError(BritiveBadRequestException):
    pass


class ResourceProfileCheckOutError(BritiveBadRequestException):
    pass


class ResourceProfileCheckInNotAllowedError(BritiveBadRequestException):
    pass


class ResourceInvalidTransactionError(BritiveBadRequestException):
    pass


class ResourceUnauthorizedCheckInError(BritiveBadRequestException):
    pass


class ResourceMissingAssociationsError(BritiveBadRequestException):
    pass


class ResourceMissingPermissionVariableError(BritiveBadRequestException):
    pass


class ResourcePermissionNotExistError(BritiveBadRequestException):
    pass


class ResourceLabelKeyMissingError(BritiveBadRequestException):
    pass


class ResourceProfileMissingError(BritiveBadRequestException):
    pass


class ResourceTypeMissingError(BritiveBadRequestException):
    pass


class ResponseTemplateMissingError(BritiveBadRequestException):
    pass


class ResourceVariablePermissionMissingError(BritiveBadRequestException):
    pass


class ResourceProfilePermissionExistsError(BritiveBadRequestException):
    pass


class ResourceProfilePermissionTypeMismatchError(BritiveBadRequestException):
    pass


class ResourcePermissionNotAddableError(BritiveBadRequestException):
    pass


class UsernameFormatValidationError(BritiveBadRequestException):
    pass


class UserPropertiesReadError(BritiveBadRequestException):
    pass


class UserModificationError(BritiveBadRequestException):
    pass


class UserCreationError(BritiveBadRequestException):
    pass


class UserUpdateError(BritiveBadRequestException):
    pass


class UserDeletionError(BritiveBadRequestException):
    pass


class UserDisableError(BritiveBadRequestException):
    pass


class UserEnableError(BritiveBadRequestException):
    pass


class UserAlreadyExistsError(BritiveBadRequestException):
    pass


class UserPasswordResetError(BritiveBadRequestException):
    pass


class UserMfaResetError(BritiveBadRequestException):
    pass


class UserTagCreationError(BritiveBadRequestException):
    pass


class UserTagModificationError(BritiveBadRequestException):
    pass


class UserTagReadError(BritiveBadRequestException):
    pass


class UserTagAddError(BritiveBadRequestException):
    pass


class UserTagAddDuplicateError(BritiveBadRequestException):
    pass


class UserTagRemoveError(BritiveBadRequestException):
    pass


class UserTagDisableError(BritiveBadRequestException):
    pass


class UserTagEnableError(BritiveBadRequestException):
    pass


class UserTagDeletionError(BritiveBadRequestException):
    pass


class UserTagUpdateError(BritiveBadRequestException):
    pass


class ReportLoadError(BritiveBadRequestException):
    pass


class MfaDisableAllUsersError(BritiveBadRequestException):
    pass


class GenericError(BritiveBadRequestException):
    pass


bad_request_code_map = {
    # Application related
    'A-0001': ApplicationCreationError,
    'A-0002': ApplicationPropertiesReadError,
    'A-0003': ApplicationUpdateError,
    'A-0004': ApplicationDeletionError,
    'A-0005': ApplicationSavePropertiesError,
    # Advanced settings related
    'AS-0001': MissingJustificationError,
    'AS-0002': InvalidJustificationError,
    'AS-0003': MissingTicketError,
    'AS-0004': MissingTicketTypeError,
    'AS-0005': MissingTicketIdError,
    'AS-0006': InvalidTicketTypeError,
    'AS-0007': InvalidTicketIdError,
    # API token related
    'AT-0001': ApiTokenCreationError,
    'AT-0002': ApiTokenUpdateError,
    'AT-0003': ApiTokenDeletionError,
    # Application-specific profile check-in related
    'CI-0001': AwsProfileCheckInError,
    'CI-0002': AzureProfileCheckInError,
    'CI-0003': GcpProfileCheckInError,
    'CI-0004': OracleProfileCheckInError,
    'CI-0005': SalesForceProfileCheckInError,
    'CI-0006': ServiceNowProfileCheckInError,
    'CI-0007': OktaProfileCheckInError,
    'CI-0008': SnowflakeProfileCheckInError,
    'CI-0009': BritiveProfileCheckInError,
    'CI-0010': AwsIdentityCenterProfileCheckInError,
    # Application-specific profile checkout related
    'CO-0001': AwsProfileCheckOutError,
    'CO-0002': AzureProfileCheckOutError,
    'CO-0003': GcpProfileCheckOutError,
    'CO-0004': OracleProfileCheckOutError,
    'CO-0005': SalesForceProfileCheckOutError,
    'CO-0006': ServiceNowProfileCheckOutError,
    'CO-0007': OktaProfileCheckOutError,
    'CO-0008': SnowflakeProfileCheckOutError,
    'CO-0009': BritiveProfileCheckOutError,
    'CO-0010': AwsIdentityCenterProfileCheckOutError,
    # My Access related
    'MA-0001': ProfileCheckInError,
    'MA-0002': ProfileCheckOutError,
    'MA-0003': ProfileStatusReadError,
    'MA-0004': ProfileStatusUpdateError,
    'MA-0005': ProfileSharedAccountsReadError,
    'MA-0006': ProfileSnapshotDeletionError,
    'MA-0007': ProfileSnapshotCreationError,
    'MA-0008': ProfileAlreadyCheckedInError,
    'MA-0009': ApprovalJustificationRequiredError,
    'MA-0010': ProfileApprovalRequiredError,
    'MA-0011': PendingProfileApprovalRequestError,
    # Profile management related
    'P-0001': ProfileCreationError,
    'P-0002': ProfileReadError,
    'P-0003': ProfileUpdateError,
    'P-0004': ProfileDeletionError,
    'P-0005': ProfileValidationError,
    # Profile Favorites related
    'PF-0001': ProfileFavoriteSaveError,
    'PF-0002': ProfileFavoriteDeleteError,
    'PF-0003': ProfileFavoriteReadError,
    # Profile Policy related
    'PP-0001': ProfilePolicyPermissionsError,
    'PP-0002': ProfilePolicyInvalidTokenError,
    'PP-0003': ProfilePolicyCreationError,
    'PP-0004': ProfilePolicyUpdateError,
    'PP-0005': ProfilePolicyGenericError,
    'PP-0006': ProfilePolicyCreationUpdateError,
    # Profile request related
    'PR-0001': ProfileRequestError,
    # Access Broker related
    'RM-0001': ResourceFavoriteRemovalError,
    'RM-0002': ResourceProfileCheckOutError,
    'RM-0003': ResourceProfileCheckInNotAllowedError,
    'RM-0004': ResourceInvalidTransactionError,
    'RM-0005': ResourceUnauthorizedCheckInError,
    'RM-0006': ResourceMissingAssociationsError,
    'RM-0007': ResourceMissingPermissionVariableError,
    'RM-0008': ResourcePermissionNotExistError,
    'RM-0009': ResourceLabelKeyMissingError,
    'RM-0010': ResourceProfileMissingError,
    'RM-0011': ResourceTypeMissingError,
    'RM-0012': ResponseTemplateMissingError,
    'RM-0013': ResourceVariablePermissionMissingError,
    'RM-0014': ResourceProfilePermissionExistsError,
    'RM-0015': ResourceProfilePermissionTypeMismatchError,
    'RM-0016': ResourcePermissionNotAddableError,
    # Users related
    'U-0001': UsernameFormatValidationError,
    'U-0002': UserPropertiesReadError,
    'U-0003': UserModificationError,
    'U-0004': UserCreationError,
    'U-0005': UserUpdateError,
    'U-0006': UserDeletionError,
    'U-0007': UserDisableError,
    'U-0008': UserEnableError,
    'U-0009': UserAlreadyExistsError,
    'U-0010': UserPasswordResetError,
    'U-0011': UserMfaResetError,
    # User tags related
    'UT-0001': UserTagCreationError,
    'UT-0002': UserTagModificationError,
    'UT-0003': UserTagReadError,
    'UT-0004': UserTagAddError,
    'UT-0005': UserTagAddDuplicateError,
    'UT-0006': UserTagRemoveError,
    'UT-0007': UserTagDisableError,
    'UT-0008': UserTagEnableError,
    'UT-0009': UserTagDeletionError,
    'UT-0010': UserTagUpdateError,
    # Miscellaneous
    'R-0001': ReportLoadError,
    'IDP-0001': MfaDisableAllUsersError,
    'G-0001': GenericError,
}
