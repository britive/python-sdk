import functools
import pytest
import random
import os
import string
import random

# don't worry about these invalid references - it will be fixed up if we are running local tests
# vs running it through tox
from britive.britive import Britive
from britive import exceptions  # exceptions used in test files so including here for ease


britive = Britive()  # source details from environment variables


characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")


def generate_random_password(length=30):
    # shuffling the characters
    random.shuffle(characters)

    # picking random characters from the list
    password = []
    for i in range(length):
        password.append(random.choice(characters))

    # shuffling the resultant password
    random.shuffle(password)

    # converting the list to string
    # printing the list
    return "".join(password)


def cleanup(resource):
    file = f'./.cache/v/resources/{resource}'  # ./ instead of ../ since this is being run from the root directory
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
@cached_resource(name='user')
def cached_user(pytestconfig):
    r = str(random.randint(0, 1000000))
    user_to_create = {
        'username': f'testpythonapiwrapper{r}',
        'email': f'testpythonapiwrapper{r}@britive.com',
        'firstName': 'TestPython',
        'lastName': 'APIWrapper',
        'password': generate_random_password(),
        'status': 'active'
    }
    return britive.users.create(**user_to_create)


@pytest.fixture(scope='session')
@cached_resource(name='tag')
def cached_tag(pytestconfig):
    tag_to_create = {
        'name': f'testpythonapiwrappertag-{random.randint(0, 1000000)}'
    }
    return britive.tags.create(**tag_to_create)


@pytest.fixture(scope='session')
@cached_resource(name='service-identity')
def cached_service_identity(pytestconfig):
    service_identity_to_create = {
        'name': f'testpythonapiwrapperserviceidentity{random.randint(0, 1000000)}',
        'status': 'active'
    }
    return britive.service_identities.create(**service_identity_to_create)


@pytest.fixture(scope='session')
@cached_resource(name='service-identity-token')
def cached_service_identity_token(pytestconfig, cached_service_identity):
    return britive.service_identity_tokens.create(cached_service_identity['userId'], 90)


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
def cached_application(pytestconfig, cached_catalog):
    app_to_create = {
        'name': f'aws-pythonapiwrapper-test-{random.randint(0, 1000000)}',
        'identity_provider_name': 'BritivePythonApiWrapperTesting',
        'integration_role_name': 'britive-integration-role'
    }
    aws_standalone_catalog_id = cached_catalog['AWS Standalone-1.0']['catalogAppId']
    return britive.applications.create(
        catalog_id=aws_standalone_catalog_id,
        application_name=app_to_create['name']
    )


@pytest.fixture(scope='session')
@cached_resource(name='environment-group')
def cached_environment_group(pytestconfig, cached_application):
    environment_group_to_create = {
        'name': f'Test-{random.randint(0, 1000000)}'
    }
    return britive.environment_groups.create(
            application_id=cached_application['appContainerId'],
            name=environment_group_to_create['name']
        )


@pytest.fixture(scope='session')
@cached_resource(name='environment')
def cached_environment(pytestconfig, cached_application):
    environment_to_create = {
        'name': f'Sigma Labs Test-{random.randint(0, 1000000)}'
    }
    return britive.environments.create(
            application_id=cached_application['appContainerId'],
            name=environment_to_create['name']
        )


@pytest.fixture(scope='session')
@cached_resource(name='scan')
def cached_scan(pytestconfig, cached_application, cached_environment):
    return britive.scans.scan(
            application_id=cached_application['appContainerId'],
            environment_id=cached_environment['id']
        )


@pytest.fixture(scope='session')
@cached_resource(name='account')
def cached_account(pytestconfig, cached_application, cached_environment):
    accounts = britive.accounts.list(
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
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
            application_id=cached_application['appContainerId'],
            environment_id=cached_environment['id']
        )[0]


@pytest.fixture(scope='session')
@cached_resource(name='group')
def cached_group(pytestconfig, cached_application, cached_environment):
    return britive.groups.list(
            application_id=cached_application['appContainerId'],
            environment_id=cached_environment['id']
        )[0]


@pytest.fixture(scope='session')
@cached_resource(name='identity-attribute')
def cached_identity_attribute(pytestconfig, cached_application, cached_environment):
    return britive.identity_attributes.create(
            name='test',
            description='test',
            data_type='String',
            multi_valued=False
        )


@pytest.fixture(scope='session')
@cached_resource(name='profile')
def cached_profile(pytestconfig, cached_application):
    return britive.profiles.create(
            application_id=cached_application['appContainerId'],
            name='test'
        )


@pytest.fixture(scope='session')
@cached_resource(name='static-session-attribute')
def cached_static_session_attribute(pytestconfig, cached_profile):
    return britive.profiles.session_attributes.add_static(
            profile_id=cached_profile['papId'],
            tag_name='test-static',
            tag_value='test'
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
            profile_id=cached_profile['papId'],
            identity_attribute_id=email_id,
            tag_name='test-dynamic'
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
                'scope': [
                    {
                        'type': 'Environment',
                        'value': cached_environment['id']
                    }

                ]
            }
        )


@pytest.fixture(scope='session')
@cached_resource(name='security-policy')
def cached_security_policy(pytestconfig, cached_service_identity_token):
    r = str(random.randint(0, 1000000))

    return britive.security_policies.create(
            name=f'test-{r}',
            description='test',
            ips=['1.1.1.1', '10.0.0.0/16'],
            effect='Allow',
            tokens=[cached_service_identity_token['id']]
        )


@pytest.fixture(scope='session')
@cached_resource(name='api-token')
def cached_api_token(pytestconfig, cached_service_identity_token):
    return britive.api_tokens.create(
            name='test',
            expiration_days=60
        )


@pytest.fixture(scope='session')
@cached_resource(name='identity-provider')
def cached_identity_provider(pytestconfig):
    r = str(random.randint(0, 1000000))
    return britive.identity_providers.create(name=f'pythonapiwrappertest-{r}')


@pytest.fixture(scope='session')
@cached_resource(name='scim-token')
def cached_scim_token(pytestconfig, cached_identity_provider):
    return britive.identity_providers.scim_tokens.create(
        identity_provider_id=cached_identity_provider['id'],
        token_expiration_days=60
    )


@pytest.fixture(scope='session')
@cached_resource(name='checked-out-profile')
def cached_checked_out_profile(pytestconfig, cached_profile, cached_user, cached_environment):
    # add the currently authenticated user
    user_id = britive.my_access.whoami()['userId']

    try:
        britive.profiles.identities.add(
            profile_id=cached_profile['papId'],
            user_id=user_id
        )
    except exceptions.InvalidRequest as e:
        if str(e) == 'P-0003 - User is already assigned to the profile - no further details available':
            pass

    # add a permission (just take the first in the list)
    permissions = britive.profiles.permissions.list_available(profile_id=cached_profile['papId'])

    # for AWS only 1 IAM role can be assigned in permissions so list_available returns an empty list if there is
    # already a permission assigned to the profile
    if len(permissions) > 0:
        britive.profiles.permissions.add(
            profile_id=cached_profile['papId'],
            permission_type=permissions[0]['type'],
            permission_name=permissions[0]['name']
        )

    # and now checkout the profile
    return britive.my_access.checkout(
            profile_id=cached_profile['papId'],
            environment_id=cached_environment['id'],
            include_credentials=True
        )


@pytest.fixture(scope='session')
@cached_resource(name='checked-out-profile-by-name')
def cached_checked_out_profile_by_name(pytestconfig, cached_profile, cached_user, cached_environment,
                                       cached_application):

    # note that cached_checked_out_profile has to be run first so all the permissions and user entitlements
    # are set properly. We are just re-checking out the profile using names instead of IDs here.
    # and now checkout the profile

    account_id = os.environ['BRITIVE_TEST_ENV_ACCOUNT_ID']
    return britive.my_access.checkout_by_name(
            profile_name=cached_profile['name'],
            environment_name=f'{account_id} ({cached_environment["name"]})',
            application_name=cached_application['catalogAppDisplayName'],
            include_credentials=True
        )


@pytest.fixture(scope='session')
@cached_resource(name='notification')
def cached_notification(pytestconfig):
    r = str(random.randint(0, 1000000))
    return britive.notifications.create(
            name=f'pythonapiwrappertest-{r}',
            description='test'
        )


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





