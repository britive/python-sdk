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

def test_add_association(cached_access_broker_profile):
    association = britive.access_broker.profiles.add_association(cached_access_broker_profile['profileId'], associations={'Location' : ['Oregon']})
    assert isinstance(association, dict)

def test_list_associations(cached_access_broker_profile):
    associations = britive.access_broker.profiles.list_associations(cached_access_broker_profile['profileId'])
    assert isinstance(associations, dict)
    assert len(associations) > 0

def test_get_system_values(cached_resource_type):
    system_values = britive.access_broker.profiles.get_system_values(resource_type_id=cached_resource_type['resourceTypeId'])
    assert isinstance(system_values, list)
