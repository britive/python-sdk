from .cache import *


def test_create(cached_access_broker_profile_policy):
    assert isinstance(cached_access_broker_profile_policy, dict)


def test_list(cached_access_broker_profile):
    policies = britive.access_broker.profiles.policies.list(profile_id=cached_access_broker_profile['profileId'])
    assert isinstance(policies, list)
    assert len(policies) > 0


def test_get(cached_access_broker_profile_policy, cached_access_broker_profile):
    policy = britive.access_broker.profiles.policies.get(
        policy_id=cached_access_broker_profile_policy['id'], profile_id=cached_access_broker_profile['profileId']
    )
    assert isinstance(policy, dict)


def test_update(cached_access_broker_profile_policy, cached_access_broker_profile, cached_user):
    britive.access_broker.profiles.policies.update(
        policy_id=cached_access_broker_profile_policy['id'],
        profile_id=cached_access_broker_profile['profileId'],
        name=cached_access_broker_profile_policy['name'],
        access_type=cached_access_broker_profile_policy['accessType'],
        condition=cached_access_broker_profile_policy['condition'],
        members={'users': [{'id': cached_user['userId']}]},
    )
    policy = britive.access_broker.profiles.policies.get(
        policy_id=cached_access_broker_profile_policy['id'], profile_id=cached_access_broker_profile['profileId']
    )
    assert isinstance(policy, dict)
