from .cache import *  # will also import some globals like `britive`


def test_catalog(cached_catalog):
    assert isinstance(cached_catalog, dict)
    assert 'AWS Standalone-1.0' in cached_catalog.keys()
    assert isinstance(cached_catalog['AWS Standalone-1.0'], dict)


def test_create(cached_application):
    show = None
    for prop in cached_application['catalogApplication']['propertyTypes']:
        if prop['name'] == 'showAwsAccountNumber':
            show = prop['value']
            break
    assert isinstance(cached_application, dict)
    assert show is False
    assert isinstance(cached_application['userAccountMappings'], list)
    assert len(cached_application['userAccountMappings']) == 0


def test_disable(cached_application):
    response = britive.applications.disable(application_id=cached_application['appContainerId'])
    assert isinstance(response, dict)
    assert response['status'] == 'inactive'


def test_enable(cached_application):
    response = britive.applications.enable(application_id=cached_application['appContainerId'])
    assert isinstance(response, dict)
    assert response['status'] == 'active'


def test_list(cached_application):
    apps = britive.applications.list()
    assert isinstance(apps, list)
    assert len(apps) > 0
    assert isinstance(apps[0], dict)
    assert cached_application['appContainerId'] in [a['appContainerId'] for a in apps]


def test_get(cached_application):
    app = britive.applications.get(application_id=cached_application['appContainerId'])
    assert app['appContainerId'] == cached_application['appContainerId']
    assert app['catalogAppDisplayName'] == cached_application['catalogAppDisplayName']


def test_test_failure(cached_application):
    response = britive.applications.test(application_id=cached_application['appContainerId'])
    assert isinstance(response, dict)
    assert 'success' in response.keys()
    assert 'message' in response.keys()
    assert not response['success']


def test_update(cached_application):
    tenant = britive.tenant.replace('.britive-app.com', '')
    idp = os.environ.get('BRITIVE_IDP_NAME_OVERRIDE') or f'BritivePythonApiWrapperTesting-{tenant}'
    role = os.environ.get('BRITIVE_INTEGRATION_ROLE_NAME_OVERRIDE') or f'britive-integration-role-{tenant}'

    app = britive.applications.update(
        application_id=cached_application['appContainerId'],
        showAwsAccountNumber=True,
        identityProvider=idp,
        roleName=role
    )
    show = None
    for prop in app['catalogApplication']['propertyTypes']:
        if prop['name'] == 'showAwsAccountNumber':
            show = prop['value']
            break
    assert isinstance(app, dict)
    assert show is True


def test_set_user_account_mapping(cached_application):
    app = britive.applications.set_user_account_mapping(cached_application['appContainerId'], 'email')
    assert isinstance(app['userAccountMappings'], list)
    assert len(app['userAccountMappings']) == 1
    assert app['userAccountMappings'][0]['name'] == 'email'

