from .cache import *


def test_add(cached_access_broker_profile_permission):
    assert isinstance(cached_access_broker_profile_permission, dict)


def test_list(cached_access_broker_profile):
    permissions = britive.access_broker.profiles.permissions.list_permissions(
        profile_id=cached_access_broker_profile['profileId']
    )
    assert isinstance(permissions, list)
    assert len(permissions) > 0


def test_list_available_permissions(cached_access_broker_profile):
    permissions = britive.access_broker.profiles.permissions.list_available_permissions(
        profile_id=cached_access_broker_profile['profileId']
    )
    assert isinstance(permissions, list)
