from .cache import *  # will also import some globals like `britive`


def test_list():
    response = britive.system.roles.list()
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert 'id' in response[0].keys()
    assert 'name' in response[0].keys()


def test_create(cached_system_level_role):
    assert isinstance(cached_system_level_role, dict)
    assert 'id' in cached_system_level_role.keys()
    assert 'name' in cached_system_level_role.keys()
    assert cached_system_level_role['name'].startswith('python-sdk')


def test_get_id(cached_system_level_role):
    response = britive.system.roles.get(role_identifier=cached_system_level_role['id'], identifier_type='id')
    assert 'id' in response.keys()
    assert 'name' in response.keys()
    assert response['name'].startswith('python-sdk')


def test_get_name(cached_system_level_role):
    response = britive.system.roles.get(role_identifier=cached_system_level_role['name'])
    assert 'id' in response.keys()
    assert 'name' in response.keys()
    assert response['name'].startswith('python-sdk')


def test_update_id(cached_system_level_role):
    permissions = britive.system.permissions.list()
    permission_ids = []
    permissions_to_add = ['SMAdminPermission', 'NMAdminPermission']
    for permission in permissions:
        if permission['name'] in permissions_to_add:
            permission_ids.append(permission['id'])

    role = britive.system.roles.build(
        name=cached_system_level_role['name'],
        permissions=permission_ids,
        identifier_type='id'
    )
    response = britive.system.roles.update(
        role_identifier=cached_system_level_role['id'],
        role=role,
        identifier_type='id'
    )

    assert response is None

    response = britive.system.roles.get(role_identifier=cached_system_level_role['id'], identifier_type='id')
    assert 'id' in response.keys()
    assert 'name' in response.keys()
    assert response['name'].startswith('python-sdk')
    assert len(response['permissions']) == 2


def test_update_name(cached_system_level_role):
    role = britive.system.roles.build(
        name=cached_system_level_role['name'],
        permissions=['NMAdminPermission', 'SMAdminPermission', 'ReportsViewPermission'],
        identifier_type='name'
    )
    response = britive.system.roles.update(
        role_identifier=cached_system_level_role['name'],
        role=role,
        identifier_type='name'
    )

    assert response is None

    response = britive.system.roles.get(role_identifier=cached_system_level_role['name'], identifier_type='name')
    assert 'id' in response.keys()
    assert 'name' in response.keys()
    assert response['name'].startswith('python-sdk')
    assert len(response['permissions']) == 3


def test_delete(cached_system_level_role):
    try:
        assert britive.system.roles.delete(role_identifier=cached_system_level_role['id'], identifier_type='id') is None

        with pytest.raises(exceptions.NotFound):
            britive.system.roles.get(cached_system_level_role['id'])
    finally:
        cleanup('role-system-level')

