from .cache import *

def test_create(cached_resource_permission):
    assert isinstance(cached_resource_permission, dict)

def test_list(cached_resource_type):
    permissions = britive.access_broker.resources.permissions.list(resource_type_id=cached_resource_type['resourceTypeId'])
    assert isinstance(permissions, list)
    assert len(permissions) > 0

def test_get(cached_resource_type, cached_resource_permission):
    list_perms = britive.access_broker.resources.permissions.list(resource_type_id=cached_resource_type['resourceTypeId'])
    __permission_id = None
    for permission in list_perms:
        if permission['name'] == cached_resource_permission['name']:
            __permission_id = permission['permissionId']
    if __permission_id is None:
        assert False
    permission = britive.access_broker.resources.permissions.get(permission_id=__permission_id)
    assert isinstance(permission, list)

def test_get_urls(cached_resource_type, cached_resource_permission):
    list_perms = britive.access_broker.resources.permissions.list(resource_type_id=cached_resource_type['resourceTypeId'])
    __permission_id = None
    for permission in list_perms:
        if permission['name'] == cached_resource_permission['name']:
            __permission_id = permission['permissionId']
    if __permission_id is None:
        assert False
    urls = britive.access_broker.resources.permissions.get_urls(permission_id=__permission_id)
    assert isinstance(urls, dict)

def test_update(cached_resource_permission, cached_resource_type):
    list_perms = britive.access_broker.resources.permissions.list(resource_type_id=cached_resource_type['resourceTypeId'])
    __permission_id = None
    for permission in list_perms:
        if permission['name'] == cached_resource_permission['name']:
            __permission_id = permission['permissionId']
    if __permission_id is None:
        assert False
    permission = britive.access_broker.resources.permissions.update(
        permission_id=__permission_id,
        description='test2',
        name = cached_resource_permission['name'],
        resource_type_id=cached_resource_type['resourceTypeId']
    )
    assert isinstance(permission, dict)
    assert permission['description'] == 'test2'

