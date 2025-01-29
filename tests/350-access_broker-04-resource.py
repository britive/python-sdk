from .cache import *


def test_create(cached_access_broker_resource):
    assert isinstance(cached_access_broker_resource, dict)


def test_list():
    resources = britive.access_broker.resources.list()
    assert isinstance(resources, list)
    assert len(resources) > 0


def test_get(cached_access_broker_resource):
    resource = britive.access_broker.resources.get(resource_id=cached_access_broker_resource['resourceId'])
    assert isinstance(resource, dict)


def test_update(cached_access_broker_resource, timestamp, cached_access_broker_resource_label):
    britive.access_broker.resources.update(
        resource_id=cached_access_broker_resource['resourceId'],
        description=f'{timestamp}-update',
        resource_labels={cached_access_broker_resource_label['keyName']: [f'{timestamp}-test-value']},
    )
    resource = britive.access_broker.resources.get(resource_id=cached_access_broker_resource['resourceId'])
    assert isinstance(resource, dict)
    assert resource['description'] == f'{timestamp}-update'
