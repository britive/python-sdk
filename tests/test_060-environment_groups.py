from .cache import *  # will also import some globals like `britive`


def test_environment_group_create(cached_environment_group):
    assert isinstance(cached_environment_group, dict)


def test_environment_group_list(cached_application):
    groups = britive.environment_groups.list(application_id=cached_application['appContainerId'])
    assert isinstance(groups, list)
    assert len(groups) > 0
    assert isinstance(groups[0], dict)


def test_environment_group_get(cached_application, cached_environment_group):
    group_get = britive.environment_groups.get(
        application_id=cached_application['appContainerId'], 
        environment_group_id=cached_environment_group['id']
    )
    assert isinstance(group_get, dict)
    assert group_get['name'] == cached_environment_group['name']





