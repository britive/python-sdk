from .cache import *
import random
def test_create(cached_access_broker_profile):
    assert isinstance(cached_access_broker_profile, dict)
    
def test_list():
    profiles = britive.access_broker.profiles.list()
    assert isinstance(profiles, list)
    assert len(profiles) > 0

def test_get(cached_access_broker_profile):
    profile = britive.access_broker.profiles.get(profile_id=cached_access_broker_profile['profileId'])
    assert isinstance(profile, dict)

def test_update(cached_access_broker_profile):
    britive.access_broker.profiles.update(
        profile_id=cached_access_broker_profile['profileId'],
        description="test2"
    )
    profile = britive.access_broker.profiles.get(profile_id=cached_access_broker_profile['profileId'])
    assert isinstance(profile, dict)
    assert profile['description'] == 'test2'
