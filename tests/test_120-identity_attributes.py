from .cache import *  # will also import some globals like `britive`
import os


def test_list():
    attributes = britive.identity_attributes.list()
    assert isinstance(attributes, list)
    assert len(attributes) >= 7  # there are 7 default attributes that are managed by the system


def test_create(cached_identity_attribute):
    assert isinstance(cached_identity_attribute, dict)


def test_delete(cached_identity_attribute):
    response = britive.identity_attributes.delete(attribute_id=cached_identity_attribute['id'])
    assert response is None

    # just do the cleanup here as we don't really need to persist identity attributes across
    # multiple pytest sessions
    cleanup('identity-attribute')
