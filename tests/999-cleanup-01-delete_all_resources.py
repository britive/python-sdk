# note that the order of deletes could matter here so we will delete resources
# in the opposite order of creation.
from time import sleep

from britive import exceptions

from .cache import *  # will also import some globals like `britive`


# 500-audit_logs
def test_audit_logs_webhook_delete(cached_notification_medium_webhook):
    try:
        response = britive.audit_logs.webhooks.delete(notification_medium_id=cached_notification_medium_webhook['id'])
        assert response is None
    except exceptions.InvalidRequest as e:
        assert 'Auditlog webhook not found' in str(e)
    finally:
        cleanup('audit-logs-webhook')


# 350-access_broker
def test_delete_access_broker_profile_permission(cached_access_broker_profile_permission, cached_access_broker_profile):
    try:
        response = britive.access_broker.profiles.permissions.delete_permission(
            permission_id=cached_access_broker_profile_permission['permissionId'],
            profile_id=cached_access_broker_profile['profileId'],
        )
        assert response is None
    finally:
        cleanup('access-broker-profile-permission')


def test_delete_access_broker_profile_policy(cached_access_broker_profile_policy, cached_access_broker_profile):
    try:
        response = britive.access_broker.profiles.policies.delete(
            policy_id=cached_access_broker_profile_policy['id'], profile_id=cached_access_broker_profile['profileId']
        )
        assert response is None
    finally:
        cleanup('access-broker-profile-policy')


def test_delete_access_broker_profile(cached_access_broker_profile):
    try:
        response = britive.access_broker.profiles.delete(cached_access_broker_profile['profileId'])
        assert response is None
    finally:
        cleanup('access-broker-profile')


def test_delete_access_broker_resource(cached_access_broker_resource):
    try:
        response = britive.access_broker.resources.delete(cached_access_broker_resource['resourceId'])
        assert response is None
    finally:
        cleanup('access-broker-resource')


def test_delete_resource_label(cached_access_broker_resource_label):
    try:
        response = britive.access_broker.resources.labels.delete(cached_access_broker_resource_label['keyId'])
        assert response is None
    finally:
        cleanup('access-broker-resource-label')


def test_delete_resource_type(cached_access_broker_resource_type):
    remaining_permissions = britive.access_broker.resources.permissions.list(
        resource_type_id=cached_access_broker_resource_type['resourceTypeId']
    )
    for permission in remaining_permissions:
        try:
            response = britive.access_broker.resources.permissions.delete(permission['permissionId'])
            assert response is None
        except exceptions.NotFound as e:
            assert 'Resource permission does not exist' in str(e)
    try:
        response = britive.access_broker.resources.types.delete(cached_access_broker_resource_type['resourceTypeId'])
        assert response is None
    except exceptions.InvalidRequest as e:
        assert 'Resource type does not exist' in str(e)
    finally:
        cleanup('access-broker-resource-type')


def test_response_template_delete(cached_access_broker_response_template):
    try:
        response = britive.access_broker.response_templates.delete(cached_access_broker_response_template['templateId'])
        assert response is None
    finally:
        cleanup('access-broker-response-template')


# 250-system
def test_system_level_permission_delete(cached_system_level_permission):
    try:
        response = britive.system.permissions.delete(cached_system_level_permission['id'])
        assert response is None
    finally:
        cleanup('permission-system-level')


def test_system_level_role_delete(cached_system_level_role):
    try:
        response = britive.system.roles.delete(cached_system_level_role['id'])
        assert response is None
    finally:
        cleanup('role-system-level')


def test_system_level_policy_delete(cached_system_level_policy):
    try:
        response = britive.system.policies.delete(cached_system_level_policy['id'])
        assert response is None
    finally:
        cleanup('policy-system-level')


def test_system_level_policy_condition_as_default_json_str_delete(
    cached_system_level_policy_condition_as_default_json_str,
):
    try:
        response = britive.system.policies.delete(cached_system_level_policy_condition_as_default_json_str['id'])
        assert response is None
    finally:
        cleanup('policy-system-level-condition-default-as-json-str')


def test_system_level_policy_condition_as_dictionary_delete(cached_system_level_policy_condition_as_dictionary):
    try:
        response = britive.system.policies.delete(cached_system_level_policy_condition_as_dictionary['id'])
        assert response is None
    finally:
        cleanup('policy-system-level-condition-as-dict')


# 200-application_management
def test_access_builder_associations_delete(cached_application, cached_access_builder_associations):
    try:
        response = britive.access_builder.associations.delete(
            application_id=cached_application['appContainerId'],
            association_id=cached_access_builder_associations['associationApproversSummary'][0]['id'],
        )
        assert response is None
    finally:
        cleanup('access-builder-associations')


def test_access_builder_approvers_groups_delete(cached_application, cached_access_builder_approvers_groups):
    try:
        response = britive.access_builder.approvers_groups.delete(
            application_id=cached_application['appContainerId'],
            group_id=cached_access_builder_approvers_groups.get('id'),
        )
        assert response is None
    finally:
        cleanup('access-builder-approvers-groups')


def test_add_notification_to_access_builder_delete(cached_application, cached_add_notification_to_access_builder):
    try:
        response = britive.access_builder.notifications.update(
            cached_application['appContainerId'], notification_mediums=[]
        )
        assert response is None
    except exceptions.InvalidRequest as e:
        assert 'Access builder setting does not exist' in str(e)
    finally:
        cleanup('access-builder-approvers-groups')


def test_profile_approval_policy_delete(cached_profile, cached_profile_approval_policy):
    try:
        response = britive.profiles.policies.delete(
            profile_id=cached_profile['papId'], policy_id=cached_profile_approval_policy['id']
        )
        assert response is None
    finally:
        cleanup('profile-approval-policy')


def test_profile_policy_condition_as_dict_delete(cached_profile, cached_profile_policy_condition_as_dict):
    try:
        response = britive.profiles.policies.delete(
            profile_id=cached_profile['papId'], policy_id=cached_profile_policy_condition_as_dict['id']
        )
        assert response is None
    finally:
        cleanup('profile-policy-dict')


def test_profile_policy_condition_as_json_str_delete(cached_profile, cached_profile_policy_condition_as_json_str):
    try:
        response = britive.profiles.policies.delete(
            profile_id=cached_profile['papId'], policy_id=cached_profile_policy_condition_as_json_str['id']
        )
        assert response is None
    finally:
        cleanup('profile-policy-str')


def test_profile_policy_delete(cached_profile, cached_profile_policy):
    try:
        response = britive.profiles.policies.delete(
            profile_id=cached_profile['papId'], policy_id=cached_profile_policy['id']
        )
        assert response is None
    finally:
        cleanup('profile-policy')


def test_profile_delete(cached_profile):
    try:
        response = britive.profiles.delete(
            application_id=cached_profile['appContainerId'], profile_id=cached_profile['papId']
        )

        profiles = britive.profiles.list(application_id=cached_profile['appContainerId'])

        assert response is None
        assert cached_profile['papId'] not in [p['papId'] for p in profiles]
    finally:
        cleanup('profile')
        cleanup('dynamic-session-attribute')
        cleanup('static-session-attribute')


def test_environment_delete(cached_application, cached_environment):
    try:
        response = britive.environments.delete(
            application_id=cached_application['appContainerId'], environment_id=cached_environment['id']
        )
        assert response is None
    finally:
        cleanup('environment')
        cleanup('scan')


def test_environment_group_delete(cached_application, cached_environment_group):
    try:
        groups = britive.environment_groups.list(application_id=cached_application['appContainerId'])
        num_root_groups = 0
        for group in groups:
            if group['parentId'] != '':  # cannot delete root groups - error A-0003 is thrown when attempting
                response = britive.environment_groups.delete(
                    application_id=cached_application['appContainerId'],
                    environment_group_id=cached_environment_group['id'],
                )
                assert response is None
            else:
                num_root_groups += 1
        groups = britive.environment_groups.list(application_id=cached_application['appContainerId'])
        assert isinstance(groups, list)
        assert len(groups) == num_root_groups  # the root group will remain
        assert isinstance(groups[0], dict)
    finally:
        cleanup('environment-group')


def test_application_delete(cached_application):
    try:
        while True:
            try:
                response = britive.applications.delete(application_id=cached_application['appContainerId'])
                break
            except exceptions.InvalidRequest:
                sleep(5)
        assert response is None
    finally:
        cleanup('application')
        cleanup('catalog')
        cleanup('account')
        cleanup('group')
        cleanup('permission')
        cleanup('task-service')


# 150-secrets_manager
def test_folder_delete(cached_folder, cached_vault):
    try:
        response = britive.secrets_manager.folders.delete(path=cached_folder['path'], vault_id=cached_vault['id'])
        assert response is None
    finally:
        cleanup('folder')


def test_secret_delete(cached_secret, cached_vault):
    try:
        response = britive.secrets_manager.secrets.delete(path=cached_secret['path'], vault_id=cached_vault['id'])
        assert response is None
    finally:
        cleanup('secret')


def test_static_secret_templates_delete(cached_static_secret_template):
    try:
        response = britive.secrets_manager.static_secret_templates.delete(cached_static_secret_template['id'])
        assert response is None
    finally:
        cleanup('static-secret-templates')


def test_password_policies_delete(cached_password_policies):
    try:
        response = britive.secrets_manager.password_policies.delete(cached_password_policies['id'])
        assert response is None
    finally:
        cleanup('password-policies')


def test_pin_policy_delete(cached_pin_policies):
    try:
        response = britive.secrets_manager.password_policies.delete(cached_pin_policies['id'])
        assert response is None
    finally:
        cleanup('pin-policies')


def test_policy_delete(cached_policy):
    try:
        response = britive.secrets_manager.policies.delete(cached_policy['id'])
        assert response is None
    finally:
        cleanup('policy')


def test_vault_delete(cached_vault):
    try:
        if cached_vault.get('DONOTDELETE'):
            assert True
        else:
            response = britive.secrets_manager.vaults.delete(cached_vault['id'])
            assert response is None
    finally:
        cleanup('vault')


# 100-identity_management
def test_workload_identity_provider_aws_delete(cached_workload_identity_provider_aws):
    try:
        response = britive.workload.identity_providers.delete(cached_workload_identity_provider_aws['id'])
        assert response is None
    finally:
        cleanup('workload-identity-provider-aws')


def test_workload_identity_provider_oidc_delete(cached_workload_identity_provider_oidc):
    try:
        response = britive.workload.identity_providers.delete(cached_workload_identity_provider_oidc['id'])
        assert response is None
    finally:
        cleanup('workload-identity-provider-oidc')


def test_service_identities_delete(cached_service_identity, cached_service_identity_federated):
    try:
        for si in [cached_service_identity, cached_service_identity_federated]:
            response = britive.service_identities.delete(service_identity_id=si['userId'])
            assert response is None
            assert not britive.service_identities.get_by_name(name=si['name'])
    except exceptions.NotFound:
        pass
    finally:
        cleanup('service-identity')
        cleanup('service-identity-federated')
        cleanup('service-identity-token')
        cleanup('service-identity-token-updated')


def test_tags_delete(cached_tag):
    try:
        response = britive.tags.delete(cached_tag['userTagId'])
        assert response is None
    finally:
        cleanup('tag')


def test_user_delete(cached_user):
    try:
        response = britive.users.delete(user_id=cached_user['userId'])
        assert response is None
        users = britive.users.get_by_name(name=cached_user['lastName'])
        assert isinstance(users, list)
        assert len(users) == 0
    finally:
        cleanup('user')


# 000-global_settings
def test_notification_medium_delete(cached_notification_medium):
    try:
        response = britive.notification_mediums.delete(cached_notification_medium['id'])
        assert response is None
    finally:
        cleanup('notification-medium')


def test_notification_medium_webhook_delete(cached_notification_medium_webhook):
    try:
        response = britive.notification_mediums.delete(cached_notification_medium_webhook['id'])
        assert response is None
    finally:
        cleanup('notification-medium-webhook')


def test_identity_attribute_delete(cached_identity_attribute):
    try:
        response = britive.identity_attributes.delete(attribute_id=cached_identity_attribute['id'])
        assert response is None
    finally:
        cleanup('identity-attribute')
