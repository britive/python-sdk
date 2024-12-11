from .cache import *


def test_create(cached_access_broker_resource_label):
    assert isinstance(cached_access_broker_resource_label, dict)


def test_get(cached_access_broker_resource_label):
    resource_label = britive.access_broker.resources.labels.get(label_id=cached_access_broker_resource_label['keyId'])
    assert isinstance(resource_label, dict)


def test_list():
    resource_labels = britive.access_broker.resources.labels.list()
    assert isinstance(resource_labels, dict)
    assert len(resource_labels) > 0


def test_update(timestamp, cached_access_broker_resource_label):
    resource_label = britive.access_broker.resources.labels.update(
        label_id=cached_access_broker_resource_label['keyId'],
        description=f'{timestamp}-update',
        values=cached_access_broker_resource_label['values'],
        name=cached_access_broker_resource_label['keyName'],
    )
    assert isinstance(resource_label, dict)
    assert resource_label['description'] == f'{timestamp}-update'
