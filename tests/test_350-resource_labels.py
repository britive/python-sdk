from .cache import *

def test_get(cached_resource_label):
    resource_label = britive.access_broker.resources.labels.get(label_id=cached_resource_label['keyId'])
    assert isinstance(resource_label, dict)

def test_create(cached_resource_label):
    assert isinstance(cached_resource_label, dict)

def test_list():
    resource_labels = britive.access_broker.resources.labels.list()
    assert isinstance(resource_labels, dict)
    assert len(resource_labels) > 0

def test_update(cached_resource_label):
    resource_label = britive.access_broker.resources.labels.update(
        label_id=cached_resource_label['keyId'],
        description='test2',
        name=cached_resource_label['keyName']
    )
    assert isinstance(resource_label, dict)
    assert resource_label['description'] == 'test2'

