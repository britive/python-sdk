from .cache import *  # will also import some globals like `britive`


def test_environment_create(cached_environment):
    assert isinstance(cached_environment, dict)


def test_environment_update(cached_application, cached_environment):
    account_id = os.environ['BRITIVE_TEST_ENV_ACCOUNT_ID']
    response = britive.environments.update(
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id'],
        accountId=account_id
    )
    assert isinstance(response, dict)
    assert 'catalogApplication' in response.keys()
    assert 'propertyTypes' in response['catalogApplication'].keys()
    account_id_response = None
    for prop in response['catalogApplication']['propertyTypes']:
        if prop['name'] == 'accountId':
            account_id_response = prop['value']
            break
    assert account_id_response == account_id


def test_environment_list_one(cached_application):
    envs = britive.environments.list(application_id=cached_application['appContainerId'])
    assert isinstance(envs, list)
    assert len(envs) == 1
    assert isinstance(envs[0], dict)


def test_environment_test(cached_application, cached_environment):
    response = britive.environments.test(
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )
    assert isinstance(response, dict)
    assert response['success']


def test_environment_get(cached_application, cached_environment):
    env = britive.environments.get(
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )
    assert isinstance(env, dict)
    assert env['environmentId'] == cached_environment['id']






