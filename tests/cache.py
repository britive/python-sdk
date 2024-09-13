import functools
import os
import random
import string
from time import time

import pytest

from britive import exceptions  # exceptions used in test files so including here for ease

# don't worry about these invalid references - it will be fixed up if we are running local tests
# vs running it through tox
from britive.britive import Britive

britive = Britive()  # source details from environment variables
scan_skip = bool(os.getenv('BRITIVE_TEST_IGNORE_SCAN'))
scan_skip_message = 'ignore scan requested'
constraints = bool(not (os.getenv('BRITIVE_GCP_TEST_APP_ID') and os.getenv('BRITIVE_TENANT') == 'engv2-ea'))
constraints_skip = 'not using engv2-ea and/or BRITIVE_GCP_TEST_APP_ID not set'
characters = list(string.ascii_letters + string.digits + '!@#$%^&*()')


def generate_random_password(length=30):
    # shuffling the characters
    random.shuffle(characters)

    # picking random characters from the list
    password = []
    while len(password) < length:
        password.append(random.choice(characters))

    # shuffling the resultant password
    random.shuffle(password)

    # converting the list to string
    # printing the list
    return ''.join(password)


def cleanup(resource):
    file = f'./.pytest_cache/v/resources/{resource}'  # ./ instead of ../ since this is being run from root directory
    if os.path.isfile(file):
        os.remove(file)


def cached_resource(name):
    def decorator_cached_resource(func):
        @functools.wraps(func)
        def wrapper(pytestconfig, *args, **kwargs):
            resource = pytestconfig.cache.get(f'resources/{name}', None)
            if not resource:
                resource = func(pytestconfig, *args, **kwargs)
                pytestconfig.cache.set(f'resources/{name}', resource)
            return resource

        return wrapper

    return decorator_cached_resource


@pytest.fixture(scope='session')
@cached_resource(name='timestamp')
def timestamp(pytestconfig):
    return int(time())


@pytest.fixture(scope='session')
@cached_resource(name='user')
def cached_user(pytestconfig, timestamp):
    user_to_create = {
        'username': f'testpythonapiwrapper{timestamp}',
        'email': f'testpythonapiwrapper{timestamp}@britive.com',
        'firstName': 'TestPython',
        'lastName': timestamp,
        'password': generate_random_password(),
        'status': 'active',
    }
    return britive.users.create(**user_to_create)


@pytest.fixture(scope='session')
@cached_resource(name='tag')
def cached_tag(pytestconfig, timestamp):
    tag_to_create = {'name': f'testpythonapiwrappertag-{timestamp}'}
    return britive.tags.create(**tag_to_create)


@pytest.fixture(scope='session')
@cached_resource(name='service-identity')
def cached_service_identity(pytestconfig, timestamp):
    service_identity_to_create = {
        'name': f'testpythonapiwrapperserviceidentity{timestamp}',
        'status': 'active',
    }
    return britive.service_identities.create(**service_identity_to_create)


@pytest.fixture(scope='session')
@cached_resource(name='service-identity-token')
def cached_service_identity_token(pytestconfig, cached_service_identity):
    return britive.service_identity_tokens.create(cached_service_identity['userId'], 90)


@pytest.fixture(scope='session')
@cached_resource(name='service-identity-token-updated')
def cached_service_identity_token_updated(pytestconfig, cached_service_identity):
    return britive.service_identity_tokens.update(cached_service_identity['userId'], 45)


@pytest.fixture(scope='session')
@cached_resource(name='catalog')
def cached_catalog(pytestconfig):
    apps = britive.applications.catalog()
    catalog = {}
    for app in apps:
        catalog[app['key']] = app
    return catalog


@pytest.fixture(scope='session')
@cached_resource(name='application')
def cached_application(pytestconfig, timestamp, cached_catalog):
    aws_standalone_catalog_id = cached_catalog['AWS Standalone-1.0']['catalogAppId']
    return britive.applications.create(
        catalog_id=aws_standalone_catalog_id, application_name=f'aws-pythonapiwrapper-test-{timestamp}'
    )


@pytest.fixture(scope='session')
@cached_resource(name='application-updated')
def cached_application_updated(pytestconfig, cached_catalog):
    return britive.applications.update(application_id=cached_application['appContainerId'], region='us-east-1')


@pytest.fixture(scope='session')
@cached_resource(name='environment-group')
def cached_environment_group(pytestconfig, timestamp, cached_application):
    environment_group_to_create = {'name': f'Test-{timestamp}'}
    return britive.environment_groups.create(
        application_id=cached_application['appContainerId'], name=environment_group_to_create['name']
    )


@pytest.fixture(scope='session')
@cached_resource(name='environment')
def cached_environment(pytestconfig, timestamp, cached_application):
    environment_to_create = {'name': f'Sigma Labs Test-{timestamp}'}
    return britive.environments.create(
        application_id=cached_application['appContainerId'], name=environment_to_create['name']
    )


@pytest.fixture(scope='session')
@cached_resource(name='scan')
def cached_scan(pytestconfig, cached_application, cached_environment):
    return britive.scans.scan(
        application_id=cached_application['appContainerId'], environment_id=cached_environment['id']
    )


@pytest.fixture(scope='session')
@cached_resource(name='account')
def cached_account(pytestconfig, cached_application, cached_environment):
    accounts = britive.accounts.list(
        application_id=cached_application['appContainerId'], environment_id=cached_environment['id']
    )

    # lets just grab the first account which has permissions associated with it
    # so when we test permissions we will get a response
    for account in accounts:
        if len(account['permissions']) > 0:
            return account
    return None


@pytest.fixture(scope='session')
@cached_resource(name='permission')
def cached_permission(pytestconfig, cached_application, cached_environment):
    return britive.permissions.list(
        application_id=cached_application['appContainerId'], environment_id=cached_environment['id']
    )[0]


@pytest.fixture(scope='session')
@cached_resource(name='group')
def cached_group(pytestconfig, cached_application, cached_environment):
    return britive.groups.list(
        application_id=cached_application['appContainerId'], environment_id=cached_environment['id']
    )[0]


@pytest.fixture(scope='session')
@cached_resource(name='identity-attribute')
def cached_identity_attribute(pytestconfig, timestamp):
    return britive.identity_attributes.create(
        name=f'python-sdk-test-{timestamp}', description='test', data_type='String', multi_valued=False
    )


@pytest.fixture(scope='session')
@cached_resource(name='profile')
def cached_profile(pytestconfig, timestamp, cached_application):
    return britive.profiles.create(application_id=cached_application['appContainerId'], name=f'test-{timestamp}')


@pytest.fixture(scope='session')
@cached_resource(name='profile-policy')
def cached_profile_policy(pytestconfig, cached_profile, cached_tag):
    policy = britive.profiles.policies.build(
        name=cached_profile['papId'],
        description=cached_tag['name'],
        tags=[cached_tag['name']],
        stepup_auth=True,
        always_prompt_stepup_auth=False,
    )
    return britive.profiles.policies.create(profile_id=cached_profile['papId'], policy=policy)


@pytest.fixture(scope='session')
@cached_resource(name='profile-policy-str')
def cached_profile_policy_condition_as_json_str(pytestconfig, cached_profile, cached_tag):
    policy = britive.profiles.policies.build(
        name=f"{cached_profile['papId']}_json",
        description=cached_tag['name'],
        tags=[cached_tag['name']],
        ips=['12.12.12.12', '13.13.13.13'],
        condition_as_dict=False,
    )
    return britive.profiles.policies.create(profile_id=cached_profile['papId'], policy=policy)


@pytest.fixture(scope='session')
@cached_resource(name='profile-policy-dict')
def cached_profile_policy_condition_as_dict(pytestconfig, cached_profile, cached_tag):
    policy = britive.profiles.policies.build(
        name=f"{cached_profile['papId']}_dict",
        description=cached_tag['name'],
        tags=[cached_tag['name']],
        ips=['12.12.12.12', '13.13.13.13'],
        condition_as_dict=True,
    )
    return britive.profiles.policies.create(profile_id=cached_profile['papId'], policy=policy)


@pytest.fixture(scope='session')
@cached_resource(name='profile-approval-policy')
def cached_profile_approval_policy(pytestconfig, cached_profile, cached_service_identity):
    policy = britive.profiles.policies.build(
        name=f"{cached_profile['papId']}-2",
        description='',
        service_identities=[cached_service_identity['username']],
        approval_notification_medium='Email',
        approver_users=[britive.my_access.whoami()['username']],
    )
    return britive.profiles.policies.create(profile_id=cached_profile['papId'], policy=policy)


@pytest.fixture(scope='session')
@cached_resource(name='static-session-attribute')
def cached_static_session_attribute(pytestconfig, cached_profile):
    return britive.profiles.session_attributes.add_static(
        profile_id=cached_profile['papId'], tag_name='test-static', tag_value='test'
    )


@pytest.fixture(scope='session')
@cached_resource(name='dynamic-session-attribute')
def cached_dynamic_session_attribute(pytestconfig, cached_profile):
    attributes = britive.identity_attributes.list()
    email_id = None
    for attribute in attributes:
        if attribute['builtIn'] and attribute['name'] == 'Email':
            email_id = attribute['id']
            break

    return britive.profiles.session_attributes.add_dynamic(
        profile_id=cached_profile['papId'], identity_attribute_id=email_id, tag_name='test-dynamic'
    )


@pytest.fixture(scope='session')
@cached_resource(name='task-service')
def cached_task_service(pytestconfig, cached_application):
    return britive.task_services.get(application_id=cached_application['appContainerId'])


@pytest.fixture(scope='session')
@cached_resource(name='task')
def cached_task(pytestconfig, cached_task_service, cached_application, cached_environment):
    return britive.tasks.create(
        task_service_id=cached_task_service['taskServiceId'],
        name='test',
        frequency_type='Monthly',
        start_time='01:00',
        frequency_interval='31',
        properties={
            'appId': cached_application['appContainerId'],
            'orgScan': False,
            'scope': [{'type': 'Environment', 'value': cached_environment['id']}],
        },
    )


@pytest.fixture(scope='session')
@cached_resource(name='security-policy')
def cached_security_policy(pytestconfig, timestamp, cached_service_identity_token_updated):
    return britive.security_policies.create(
        name=f'test-{timestamp}',
        description='test',
        ips=['1.1.1.1', '10.0.0.0/16'],
        effect='Allow',
        tokens=[cached_service_identity_token_updated['id']],
    )


@pytest.fixture(scope='session')
@cached_resource(name='api-token')
def cached_api_token(pytestconfig, timestamp):
    return britive.api_tokens.create(name=f'test-{timestamp}', expiration_days=60)


@pytest.fixture(scope='session')
@cached_resource(name='identity-provider')
def cached_identity_provider(pytestconfig, timestamp):
    return britive.identity_providers.create(name=f'pythonapiwrappertest-{timestamp}')


@pytest.fixture(scope='session')
@cached_resource(name='scim-token')
def cached_scim_token(pytestconfig, cached_identity_provider):
    return britive.identity_providers.scim_tokens.create(
        identity_provider_id=cached_identity_provider['id'], token_expiration_days=60
    )


@pytest.fixture(scope='session')
@cached_resource(name='checked-out-profile')
def cached_checked_out_profile(pytestconfig, cached_profile, cached_environment, cached_tag):
    # add the currently authenticated user

    calling_user_details = britive.my_access.whoami()

    policy = britive.profiles.policies.build(
        name=cached_profile['papId'],
        users=[calling_user_details['username']],
        description=cached_tag['name'],
    )
    britive.profiles.policies.create(profile_id=cached_profile['papId'], policy=policy)

    # add a permission (just take the first in the list)
    permissions = britive.profiles.permissions.list_available(profile_id=cached_profile['papId'])

    # for AWS only 1 IAM role can be assigned in permissions so list_available returns an empty list if there is
    # already a permission assigned to the profile
    if len(permissions) > 0:
        britive.profiles.permissions.add(
            profile_id=cached_profile['papId'],
            permission_type=permissions[0]['type'],
            permission_name=permissions[0]['name'],
        )

    # and now checkout the profile
    return britive.my_access.checkout(
        profile_id=cached_profile['papId'], environment_id=cached_environment['id'], include_credentials=True
    )


@pytest.fixture(scope='session')
@cached_resource(name='checked-out-profile-by-name')
def cached_checked_out_profile_by_name(pytestconfig, cached_profile, cached_environment, cached_application):
    # note that cached_checked_out_profile has to be run first so all the permissions and user entitlements
    # are set properly. We are just re-checking out the profile using names instead of IDs here.
    # and now checkout the profile

    account_id = os.environ['BRITIVE_TEST_ENV_ACCOUNT_ID']
    return britive.my_access.checkout_by_name(
        profile_name=cached_profile['name'],
        environment_name=f'{account_id} ({cached_environment["name"]})',
        application_name=cached_application['catalogAppDisplayName'],
        include_credentials=True,
    )


@pytest.fixture(scope='session')
@cached_resource(name='notification')
def cached_notification(pytestconfig, timestamp):
    return britive.notifications.create(name=f'pythonapiwrappertest-{timestamp}', description='test')


@pytest.fixture(scope='session')
@cached_resource(name='notification-available-rules')
def cached_notification_rules(pytestconfig):
    return britive.notifications.available_rules()


@pytest.fixture(scope='session')
@cached_resource(name='notification-available-users')
def cached_notification_users(pytestconfig, cached_notification):
    return britive.notifications.available_users(notification_id=cached_notification['notificationId'])


@pytest.fixture(scope='session')
@cached_resource(name='notification-available-user-tags')
def cached_notification_user_tags(pytestconfig, cached_notification):
    return britive.notifications.available_user_tags(notification_id=cached_notification['notificationId'])


@pytest.fixture(scope='session')
@cached_resource(name='notification-available-applications')
def cached_notification_applications(pytestconfig, cached_notification):
    return britive.notifications.available_applications(notification_id=cached_notification['notificationId'])


@pytest.fixture(scope='session')
@cached_resource(name='vault')
def cached_vault(pytestconfig, timestamp, cached_tag):
    try:
        vault = britive.secrets_manager.vaults.create(name=f'vault-{timestamp}', tags=[cached_tag['userTagId']])
    except exceptions.InvalidRequest:
        vault = {'DONOTDELETE': True, **britive.secrets_manager.vaults.list()}
    return vault


@pytest.fixture(scope='session')
@cached_resource(name='folder')
def cached_folder(pytestconfig, timestamp, cached_vault):
    return britive.secrets_manager.folders.create(name=f'folder-{timestamp}', vault_id=cached_vault['id'])


@pytest.fixture(scope='session')
@cached_resource(name='password-policies')
def cached_password_policies(pytestconfig, timestamp):
    return britive.secrets_manager.password_policies.create(name=f'pytestpwdpolicy-{timestamp}')


@pytest.fixture(scope='session')
@cached_resource(name='pin-policies')
def cached_pin_policies(pytestconfig, timestamp):
    return britive.secrets_manager.password_policies.create_pin(name=f'pytestpinpolicy-{timestamp}')


@pytest.fixture(scope='session')
@cached_resource(name='static-secret-templates')
def cached_static_secret_template(pytestconfig, timestamp, cached_password_policies):
    return britive.secrets_manager.static_secret_templates.create(
        name=f'test_name-{timestamp}',
        password_policy_id=cached_password_policies['id'],
        parameters={
            'name': 'Note',
            'description': f'test_template-{timestamp}',
            'mask': False,
            'required': False,
            'type': 'singleLine',
        },
    )


@pytest.fixture(scope='session')
@cached_resource(name='secret')
def cached_secret(pytestconfig, timestamp, cached_vault, cached_static_secret_template):
    return britive.secrets_manager.secrets.create(
        name=f'test_secret-{timestamp}',
        vault_id=cached_vault['id'],
        static_secret_template_id=cached_static_secret_template['id'],
    )


@pytest.fixture(scope='session')
@cached_resource(name='policy')
def cached_policy(pytestconfig, timestamp):
    policy = britive.secrets_manager.policies.build(f'pytestpolicy-{timestamp}', draft=True, active=False)
    return britive.secrets_manager.policies.create(policy=policy, path='/')


@pytest.fixture(scope='session')
@cached_resource(name='notification-medium')
def cached_notification_medium(pytestconfig, timestamp):
    return britive.notification_mediums.create(
        notification_medium_type='teams',
        name=f'pytest-nm-{timestamp}',
        connection_parameters={'Webhook URL': 'https://www.google.com/'},
    )


@pytest.fixture(scope='session')
@cached_resource(name='access-builder-approvers-groups')
def cached_access_builder_approvers_groups(pytestconfig, timestamp, cached_application, cached_user):
    return britive.access_builder.approvers_groups.create(
        application_id=cached_application['appContainerId'],
        name=f'python-sdk-access-builder-{timestamp}',
        condition='Any',
        member_list=[{'id': cached_user['userId'], 'memberType': 'User'}],
    )


@pytest.fixture(scope='session')
@cached_resource(name='access-builder-approvers-groups-update')
def cached_access_builder_approvers_groups_update(
    pytestconfig, cached_application, cached_user, cached_tag, cached_access_builder_approvers_groups
):
    britive.access_builder.approvers_groups.update(
        application_id=cached_application['appContainerId'],
        group_id=cached_access_builder_approvers_groups['id'],
        name=cached_access_builder_approvers_groups['name'],
        condition='Any',
        member_list=[
            {'id': cached_user['userId'], 'memberType': 'User'},
            {'id': cached_tag['userTagId'], 'memberType': 'Tag'},
        ],
    )

    return britive.access_builder.approvers_groups.list_approvers_group_members(
        application_id=cached_application['appContainerId'],
        group_id=cached_access_builder_approvers_groups['id'],
    )


@pytest.fixture(scope='session')
@cached_resource(name='access-builder-associations')
def cached_access_builder_associations(
    pytestconfig, cached_application, cached_environment, cached_access_builder_approvers_groups
):
    associations = [{'type': 0, 'id': cached_environment['id']}]
    approvers_groups = [{'id': cached_access_builder_approvers_groups['id']}]
    britive.access_builder.associations.create(
        application_id=cached_application['appContainerId'],
        name='AccessBuilderAssociation',
        associations=associations,
        approvers_groups=approvers_groups,
    )

    return britive.access_builder.associations.list(application_id=cached_application['appContainerId'])


@pytest.fixture(scope='session')
@cached_resource(name='access-builder-associations-update')
def cached_access_builder_associations_update(
    pytestconfig,
    cached_application,
    cached_environment,
    cached_environment_group,
    cached_access_builder_approvers_groups,
    cached_access_builder_associations,
):
    associations = [
        {'type': 0, 'id': cached_environment['id']},
        {'type': 1, 'id': cached_environment_group['id']},
    ]
    approvers_groups = [{'id': cached_access_builder_approvers_groups['id']}]
    association_id = cached_access_builder_associations['associationApproversSummary'][0]['id']
    britive.access_builder.associations.update(
        application_id=cached_application['appContainerId'],
        association_id=association_id,
        associations=associations,
        approvers_groups=approvers_groups,
    )
    return britive.access_builder.associations.get(
        application_id=cached_application['appContainerId'], association_id=association_id
    )


@pytest.fixture(scope='session')
@cached_resource(name='access-builder-associations-list')
def cached_access_builder_associations_list(pytestconfig, cached_application):
    return britive.access_builder.associations.list(application_id=cached_application['appContainerId'])


@pytest.fixture(scope='session')
@cached_resource(name='access-builder-requesters')
def cached_add_requesters_to_access_builder(pytestconfig, cached_application, cached_user):
    user_tag_members = [{'id': cached_user['userId'], 'memberType': 'User', 'condition': 'Include'}]

    britive.access_builder.requesters.update(
        application_id=cached_application['appContainerId'], user_tag_members=user_tag_members
    )

    return britive.access_builder.requesters.list(application_id=cached_application['appContainerId'])


@pytest.fixture(scope='session')
@cached_resource(name='access-builder-notifications')
def cached_add_notification_to_access_builder(pytestconfig, cached_application, cached_notification_medium):
    notification_medium = {
        'id': cached_notification_medium['id'],
        'name': cached_notification_medium['name'],
        'description': cached_notification_medium['description'],
        'application': cached_notification_medium['type'],
        'channels': cached_notification_medium.get('channels', []),
        'connectionParameters': cached_notification_medium.get('connectionParameters', {}),
    }

    britive.access_builder.notifications.update(
        application_id=cached_application['appContainerId'], notification_mediums=[notification_medium]
    )

    return britive.access_builder.notifications.list(application_id=cached_application['appContainerId'])


@pytest.fixture(scope='session')
@cached_resource(name='access-builder-enable')
def cached_enable_access_requests(pytestconfig, cached_application):
    britive.access_builder.enable(application_id=cached_application['appContainerId'])

    return britive.access_builder.get(application_id=cached_application['appContainerId'])


@pytest.fixture(scope='session')
@cached_resource(name='access-builder-disable')
def cached_disable_access_requests(pytestconfig, cached_application):
    britive.access_builder.disable(application_id=cached_application['appContainerId'])

    return britive.access_builder.get(application_id=cached_application['appContainerId'])


@pytest.fixture(scope='session')
@cached_resource(name='workload-identity-provider-aws')
def cached_workload_identity_provider_aws(pytestconfig, timestamp, cached_identity_attribute):
    # do this up front to avoid the exponential backoff and retry logic
    # if the aws identity provider already exists
    for idp in britive.workload.identity_providers.list():
        if idp['idpType'] == 'AWS':
            return idp

    try:
        response = britive.workload.identity_providers.create_aws(
            name=f'python-sdk-aws-{timestamp}', attributes_map={'UserId': cached_identity_attribute['id']}
        )
        return response
    except exceptions.InternalServerError:
        raise Exception('AWS provider could not be created and none found')


@pytest.fixture(scope='session')
@cached_resource(name='workload-identity-provider-oidc')
def cached_workload_identity_provider_oidc(pytestconfig, timestamp, cached_identity_attribute):
    response = britive.workload.identity_providers.create_oidc(
        name=f'python-sdk-oidc-{timestamp}',
        attributes_map={'sub': cached_identity_attribute['name']},
        issuer_url='https://id.fakedomain.com',
    )
    return response


@pytest.fixture(scope='session')
@cached_resource(name='policy-system-level')
def cached_system_level_policy(pytestconfig, timestamp, cached_tag):
    policy = britive.system.policies.build(
        name=f'python-sdk-{timestamp}', tags=[cached_tag['name']], roles=['UserViewRole']
    )
    response = britive.system.policies.create(policy=policy)
    return response


@pytest.fixture(scope='session')
@cached_resource(name='policy-system-level-condition-default-as-json-str')
def cached_system_level_policy_condition_as_default_json_str(pytestconfig, timestamp, cached_tag):
    policy = britive.system.policies.build(
        name=f'python-sdk-condition-default-{timestamp}',
        tags=[cached_tag['name']],
        roles=['UserViewRole'],
        ips=['11.11.11.11', '12.12.12.12'],
        condition_as_dict=False,
    )
    response = britive.system.policies.create(policy=policy)
    return response


@pytest.fixture(scope='session')
@cached_resource(name='policy-system-level-condition-as-dict')
def cached_system_level_policy_condition_as_dictionary(pytestconfig, timestamp, cached_tag):
    policy = britive.system.policies.build(
        name=f'python-sdk-condition-as-dict-{timestamp}',
        tags=[cached_tag['name']],
        roles=['UserViewRole'],
        ips=['11.11.11.11', '12.12.12.12'],
        condition_as_dict=True,
    )
    response = britive.system.policies.create(policy=policy)
    return response


@pytest.fixture(scope='session')
@cached_resource(name='role-system-level')
def cached_system_level_role(pytestconfig, timestamp):
    role = britive.system.roles.build(name=f'python-sdk-{timestamp}', permissions=['NMAdminPermission'])
    response = britive.system.roles.create(role=role)
    return response


@pytest.fixture(scope='session')
@cached_resource(name='permission-system-level')
def cached_system_level_permission(pytestconfig, timestamp):
    permission = britive.system.permissions.build(
        name=f'python-sdk-{timestamp}', consumer='apps', actions=['apps.app.view']
    )
    response = britive.system.permissions.create(permission=permission)
    return response


@pytest.fixture(scope='session')
@cached_resource(name='gcp-profile-bq')
def cached_gcp_profile_big_query(pytestconfig, timestamp):
    response = britive.profiles.create(
        application_id=os.getenv('BRITIVE_GCP_TEST_APP_ID'),
        name=f'test-bq-constraints-{timestamp}',
        scope=[{'type': 'EnvironmentGroup', 'value': '881409387174'}],
    )

    britive.profiles.permissions.add(
        profile_id=response['papId'], permission_name='BigQuery Admin', permission_type='role'
    )

    return response


@pytest.fixture(scope='session')
@cached_resource(name='gcp-profile-storage')
def cached_gcp_profile_storage(pytestconfig, timestamp):
    response = britive.profiles.create(
        application_id=os.getenv('BRITIVE_GCP_TEST_APP_ID'),
        name=f'test-storage-constraints-{timestamp}',
        scope=[{'type': 'EnvironmentGroup', 'value': '881409387174'}],
    )

    britive.profiles.permissions.add(
        profile_id=response['papId'], permission_name='Storage Admin', permission_type='role'
    )

    return response
