from britive.exceptions import NotFound

from .cache import *  # will also import some globals like `britive`


def test_list():
    response = britive.system.permissions.list()
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert 'id' in response[0]
    assert 'name' in response[0]


def test_create(cached_system_level_permission):
    assert isinstance(cached_system_level_permission, dict)
    assert 'id' in cached_system_level_permission
    assert 'name' in cached_system_level_permission
    assert cached_system_level_permission['name'].startswith('pysdk')


def test_get_id(cached_system_level_permission):
    response = britive.system.permissions.get(
        permission_identifier=cached_system_level_permission['id'], identifier_type='id'
    )
    assert 'id' in response
    assert 'name' in response
    assert response['name'].startswith('pysdk')


def test_get_name(cached_system_level_permission):
    response = britive.system.permissions.get(permission_identifier=cached_system_level_permission['name'])
    assert 'id' in response
    assert 'name' in response
    assert response['name'].startswith('pysdk')


def test_update_id(cached_system_level_permission):
    permission = britive.system.permissions.build(
        name=cached_system_level_permission['name'], consumer='apps', actions=['apps.app.view', 'apps.app.manage']
    )
    response = britive.system.permissions.update(
        permission_identifier=cached_system_level_permission['id'], permission=permission, identifier_type='id'
    )

    assert response is None

    response = britive.system.permissions.get(
        permission_identifier=cached_system_level_permission['id'], identifier_type='id'
    )
    assert 'id' in response
    assert 'name' in response
    assert response['name'].startswith('pysdk')
    assert len(response['actions']) == 2


def test_update_name(cached_system_level_permission):
    permission = britive.system.permissions.build(
        name=cached_system_level_permission['name'],
        consumer='apps',
        actions=['apps.app.view', 'apps.app.manage', 'apps.app.list'],
    )
    response = britive.system.permissions.update(
        permission_identifier=cached_system_level_permission['name'], permission=permission, identifier_type='name'
    )

    assert response is None

    response = britive.system.permissions.get(
        permission_identifier=cached_system_level_permission['name'], identifier_type='name'
    )
    assert 'id' in response
    assert 'name' in response
    assert response['name'].startswith('pysdk')
    assert len(response['actions']) == 3


def test_delete(cached_system_level_permission):
    try:
        assert (
            britive.system.permissions.delete(
                permission_identifier=cached_system_level_permission['id'], identifier_type='id'
            )
            is None
        )

        with pytest.raises(NotFound):
            britive.system.permissions.get(cached_system_level_permission['id'])
    finally:
        cleanup('permission-system-level')
