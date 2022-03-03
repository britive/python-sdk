# note that the order of deletes could matter here so we will delete resources
# in the opposite order of creation.

from .cache import *  # will also import some globals like `britive`
from britive import exceptions


# 130-profiles
def test_profile_delete(cached_profile):
    try:
        response = britive.profiles.delete(
            application_id=cached_profile['appContainerId'],
            profile_id=cached_profile['papId']
        )

        profiles = britive.profiles.list(application_id=cached_profile['appContainerId'])

        assert response is None
        assert cached_profile['papId'] not in [p['papId'] for p in profiles]
    finally:
        cleanup('profile')


# 070-environments
def test_environment_delete(cached_application, cached_environment):
    try:
        response = britive.environments.delete(
            application_id=cached_application['appContainerId'],
            environment_id=cached_environment['id']
        )
        assert response is None
    finally:
        cleanup('environment')
        cleanup('scan')


# 060-environment_groups
def test_environment_group_delete(cached_application, cached_environment_group):
    try:
        groups = britive.environment_groups.list(application_id=cached_application['appContainerId'])
        num_root_groups = 0
        for group in groups:
            if group['parentId'] != '':  # cannot delete root groups - error A-0003 is thrown when attempting
                response = britive.environment_groups.delete(
                    application_id=cached_application['appContainerId'],
                    environment_group_id=cached_environment_group['id']
                )
                assert response is None
            else:
                num_root_groups += 1
        groups = britive.environment_groups.list(application_id=cached_application['appContainerId'])
        assert isinstance(groups, list)
        assert len(groups) == num_root_groups  # the root group will remain
        assert isinstance(groups[0], dict)
    finally:
        cleanup('environment-group')


# 050-applications
def test_application_delete(cached_application):
    try:
        response = britive.applications.delete(application_id=cached_application['appContainerId'])
        assert response is None
    finally:
        cleanup('application')
        cleanup('catalog')
        cleanup('account')
        cleanup('group')
        cleanup('permission')
        cleanup('task-service')


# 040-service_identity_tokens
def test_service_identity_tokens_delete(cached_service_identity):
    try:
        britive.service_identities.delete(cached_service_identity['userId'])
        with pytest.raises(exceptions.InvalidRequest):
            britive.service_identity_tokens.get(cached_service_identity['userId'])
    finally:
        cleanup('service-identity-token')


# 030-service_identities
def test_service_identities_delete(cached_service_identity):
    try:
        response = britive.service_identities.delete(service_identity_id=cached_service_identity['userId'])
        assert response is None
        users = britive.service_identities.get_by_name(name=cached_service_identity['name'])
        assert isinstance(users, list)
        assert len(users) == 0
    finally:
        cleanup('service-identity')


# 020-tags
def test_tags_delete(cached_tag):
    try:
        response = britive.tags.delete(cached_tag['userTagId'])
        assert response is None
    finally:
        cleanup('tag')


# 010-users
def test_user_delete(cached_user):
    try:
        response = britive.users.delete(user_id=cached_user['userId'])
        assert response is None
        users = britive.users.get_by_name(name=cached_user['lastName'])
        assert isinstance(users, list)
        assert len(users) == 0
    finally:
        cleanup('user')



