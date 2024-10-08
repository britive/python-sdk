from .cache import *


def test_get(cached_access_broker_resource_type):
    resource_type = britive.access_broker.resources.types.get(
        resource_type_id=cached_access_broker_resource_type['resourceTypeId']
    )
    assert isinstance(resource_type, dict)


def test_create(cached_access_broker_resource_type):
    assert isinstance(cached_access_broker_resource_type, dict)


def test_list():
    resource_types = britive.access_broker.resources.types.list()
    assert isinstance(resource_types, list)
    assert len(resource_types) > 0


def test_update(cached_access_broker_resource_type):
    resource_type = britive.access_broker.resources.types.update(
        resource_type_id=cached_access_broker_resource_type['resourceTypeId'], description='test2'
    )
    assert isinstance(resource_type, dict)
    assert resource_type['description'] == 'test2'
