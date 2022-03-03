from .cache import *  # will also import some globals like `britive`


def test_list(cached_application, cached_environment):
    permissions = britive.permissions.list(
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )
    assert isinstance(permissions, list)
    assert len(permissions) > 0
    assert isinstance(permissions[0], dict)


def test_accounts(cached_application, cached_environment, cached_permission):
    accounts = britive.permissions.accounts(
        permission_id=cached_permission['appPermissionId'],
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )

    assert isinstance(accounts, list)


def test_groups(cached_application, cached_environment, cached_permission):
    groups = britive.permissions.groups(
        permission_id=cached_permission['appPermissionId'],
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )

    assert isinstance(groups, list)
