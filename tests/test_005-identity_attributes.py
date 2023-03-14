from .cache import *  # will also import some globals like `britive`
import os


def test_list():
    attributes = britive.identity_attributes.list()
    assert isinstance(attributes, list)
    assert len(attributes) >= 7  # there are 7 default attributes that are managed by the system


def test_create(cached_identity_attribute):
    assert isinstance(cached_identity_attribute, dict)

