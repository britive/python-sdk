from .cache import *


def test_create(cached_access_broker_resource_permission):
    assert isinstance(cached_access_broker_resource_permission, dict)


def test_list(cached_access_broker_resource_type):
    permissions = britive.access_broker.resources.permissions.list(
        resource_type_id=cached_access_broker_resource_type['resourceTypeId']
    )
    assert isinstance(permissions, list)
    assert len(permissions) > 0


def test_get(
    cached_access_broker_resource_type,
    cached_access_broker_resource_permission,
    cached_access_broker_resource_permission_id,
):
    permission = britive.access_broker.resources.permissions.get(
        permission_id=cached_access_broker_resource_permission_id
    )
    assert isinstance(permission, list)


def test_get_urls(
    cached_access_broker_resource_type,
    cached_access_broker_resource_permission,
    cached_access_broker_resource_permission_id,
):
    urls = britive.access_broker.resources.permissions.get_urls(
        permission_id=cached_access_broker_resource_permission_id
    )
    assert isinstance(urls, dict)


def test_update(
    cached_access_broker_resource_type,
    cached_access_broker_resource_permission,
    cached_access_broker_resource_permission_id,
    timestamp,
):
    permission = britive.access_broker.resources.permissions.update(
        checkin_time_limit=60,
        checkout_time_limit=60,
        description=f'{timestamp}-update',
        name=cached_access_broker_resource_permission['name'],
        permission_id=cached_access_broker_resource_permission_id,
        resource_type_id=cached_access_broker_resource_type['resourceTypeId'],
    )

    assert isinstance(permission, dict)
    assert permission['description'] == f'{timestamp}-update'
