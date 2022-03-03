import os

from .cache import *  # will also import some globals like `britive`


def test_create(cached_profile):
    assert isinstance(cached_profile, dict)
    assert cached_profile['name'] == 'test'
    assert len(cached_profile['scope']) == 0


def test_list(cached_profile):
    profiles = britive.profiles.list(application_id=cached_profile['appContainerId'])
    assert isinstance(profiles, list)
    assert len(profiles) == 1
    assert isinstance(profiles[0], dict)
    assert profiles[0]['name'] == 'test'


def test_get(cached_profile):
    profile = britive.profiles.get(application_id=cached_profile['appContainerId'], profile_id=cached_profile['papId'])
    assert isinstance(profile, dict)
    assert profile['name'] == 'test'


def test_update(cached_profile):
    profile = britive.profiles.update(
        application_id=cached_profile['appContainerId'],
        profile_id=cached_profile['papId'],
        description='test desc'
    )
    assert isinstance(profile, dict)
    assert profile['description'] == 'test desc'


def test_set_scopes(cached_profile, cached_environment):
    scopes = britive.profiles.set_scopes(
        profile_id=cached_profile['papId'],
        scopes= [
            {
                'type': 'Environment',
                'value': cached_environment['id']
            }
        ]
    )
    assert isinstance(scopes, list)
    assert len(scopes) == 1
    assert isinstance(scopes[0], dict)
    assert scopes[0]['value'] == cached_environment['id']


def test_disable(cached_profile):
    profile = britive.profiles.disable(
        application_id=cached_profile['appContainerId'],
        profile_id=cached_profile['papId']
    )
    assert isinstance(profile, dict)
    assert profile['status'] == 'inactive'


def test_enable(cached_profile):
    profile = britive.profiles.enable(
        application_id=cached_profile['appContainerId'],
        profile_id=cached_profile['papId']
    )
    assert isinstance(profile, dict)
    assert profile['status'] == 'active'


def test_identities_add(cached_profile, cached_user):
    user = britive.profiles.identities.add(
        profile_id=cached_profile['papId'],
        user_id=cached_user['userId']
    )
    assert isinstance(user, dict)
    assert user['userId'] == cached_user['userId']


def test_identities_list_assigned(cached_profile, cached_user):
    users = britive.profiles.identities.list_assigned(profile_id=cached_profile['papId'])
    assert isinstance(users, list)
    assert len(users) == 1
    assert users[0]['userId'] == cached_user['userId']


def test_identities_list_available(cached_profile):
    users = britive.profiles.identities.list_available(profile_id=cached_profile['papId'])
    assert isinstance(users, list)
    assert len(users) > 0


def test_identities_remove(cached_profile, cached_user):
    assert britive.profiles.identities.remove(profile_id=cached_profile['papId'], user_id=cached_user['userId']) is None


def test_session_attributes_add_static(cached_static_session_attribute):
    assert isinstance(cached_static_session_attribute, dict)


def test_session_attributes_add_dynamic(cached_dynamic_session_attribute):
    assert isinstance(cached_dynamic_session_attribute, dict)


def test_session_attributes_list(cached_profile):
    attributes = britive.profiles.session_attributes.list(profile_id=cached_profile['papId'])
    assert isinstance(attributes, list)
    assert len(attributes) == 2


def test_session_attributes_update_static(cached_profile, cached_static_session_attribute):
    attribute = britive.profiles.session_attributes.update_static(
        profile_id=cached_profile['papId'],
        attribute_id=cached_static_session_attribute['id'],
        tag_name='test-static-2',
        tag_value='test',
        transitive=True
    )
    assert attribute is None


def test_session_attributes_update_dynamic(cached_profile, cached_dynamic_session_attribute):
    attribute = britive.profiles.session_attributes.update_dynamic(
        profile_id=cached_profile['papId'],
        attribute_id=cached_dynamic_session_attribute['id'],
        identity_attribute_id='w2zQ4R9xoyrkWY4phEV9',
        tag_name='test-dynamic-2',
        transitive=True
    )
    assert attribute is None


def test_session_attributes_remove(cached_profile, cached_static_session_attribute, cached_dynamic_session_attribute):
    try:
        static = britive.profiles.session_attributes.remove(
            profile_id=cached_profile['papId'],
            attribute_id=cached_static_session_attribute['id']
        )
        assert static is None

        dynamic = britive.profiles.session_attributes.remove(
            profile_id=cached_profile['papId'],
            attribute_id=cached_dynamic_session_attribute['id']
        )
        assert dynamic is None
    finally:
        for resource in ['static', 'dynamic']:
            file = f'./.cache/v/resources/{resource}-session-attribute'
            if os.path.isfile(file):
                os.remove(file)


def test_tags_add(cached_profile, cached_tag):
    tag = britive.profiles.tags.add(
        profile_id=cached_profile['papId'],
        tag_id=cached_tag['userTagId']
    )
    assert isinstance(tag, dict)
    assert tag['userTagId'] == cached_tag['userTagId']


def test_tags_list_assigned(cached_profile, cached_tag):
    tags = britive.profiles.tags.list_assigned(profile_id=cached_profile['papId'])
    assert isinstance(tags, list)
    assert len(tags) == 1
    assert tags[0]['userTagId'] == cached_tag['userTagId']


def test_tags_list_available(cached_profile):
    tags = britive.profiles.tags.list_available(profile_id=cached_profile['papId'])
    assert isinstance(tags, list)
    assert len(tags) > 0


def test_tags_remove(cached_profile, cached_tag):
    assert britive.profiles.tags.remove(
        profile_id=cached_profile['papId'],
        tag_id=cached_tag['userTagId']
    ) is None


# TODO - test ProfilePermissions on some other non AWS application.
