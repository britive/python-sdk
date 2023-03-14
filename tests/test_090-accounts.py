import json

from .cache import *  # will also import some globals like `britive`


# starting with map so we can get a cached account to use for testing
@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_map(cached_application, cached_environment, cached_user, cached_account):
    response = britive.accounts.map(
        user_id=cached_user['userId'],
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id'],
        account_id=cached_account['accountId']
    )
    assert isinstance(response, list)
    assert len(response) > 0
    assert cached_user['userId'] in [u['userId'] for u in response]


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_mapped_users(cached_application, cached_environment, cached_user, cached_account):
    response = britive.accounts.mapped_users(
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id'],
        account_id=cached_account['accountId']
    )
    assert isinstance(response, list)
    assert len(response) > 0
    assert cached_user['userId'] in [u['userId'] for u in response]


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_users_available_to_map(cached_application, cached_environment, cached_user, cached_account):
    response = britive.accounts.users_available_to_map(
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id'],
        account_id=cached_account['accountId']
    )
    assert isinstance(response, list)
    assert len(response) > 0
    assert cached_user['userId'] not in [u['userId'] for u in response]


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_unmap(cached_application, cached_environment, cached_user, cached_account):
    response = britive.accounts.unmap(
        user_id=cached_user['userId'],
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id'],
        account_id=cached_account['accountId']
    )
    assert isinstance(response, list)
    assert cached_user['userId'] not in [u['userId'] for u in response]


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_list(cached_application, cached_environment):
    accounts = britive.accounts.list(
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )
    assert isinstance(accounts, list)
    assert len(accounts) > 0
    assert isinstance(accounts[0], dict)


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_permissions(cached_application, cached_environment, cached_account):
    permissions = britive.accounts.permissions(
        account_id=cached_account['accountId'],
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )

    assert isinstance(permissions, list)


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_groups(cached_application, cached_environment, cached_account):
    groups = britive.accounts.groups(
        account_id=cached_account['accountId'],
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )

    assert isinstance(groups, list)

