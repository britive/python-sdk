from .cache import *  # will also import some globals like `britive`


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_list(cached_application, cached_environment):
    groups = britive.accounts.list(
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )
    assert isinstance(groups, list)
    assert len(groups) > 0
    assert isinstance(groups[0], dict)


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_permissions(cached_application, cached_environment, cached_group):
    permissions = britive.groups.permissions(
        group_id=cached_group['appPermissionId'],
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )

    assert isinstance(permissions, list)


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_accounts(cached_application, cached_environment, cached_group):
    groups = britive.groups.accounts(
        group_id=cached_group['appPermissionId'],
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )

    assert isinstance(groups, list)
