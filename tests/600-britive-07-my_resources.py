import json
from contextlib import ExitStack

from .cache import *  # will also import some globals like `britive`


def _delete_resource_type(access_broker, resource_type_id):
    # Use the SDK permission listing rather than carrying forward the PR's pagination workaround.
    for permission in access_broker.resources.permissions.list(resource_type_id):
        access_broker.resources.permissions.delete(permission['permissionId'])
    access_broker.resources.types.delete(resource_type_id)


@pytest.fixture(scope='module')
def resource_setup():
    access_broker = britive.access_broker
    me = britive.my_access.whoami()
    suffix = int(time() * 1_000_000)
    with ExitStack() as cleanup:
        label = access_broker.resources.labels.create(
            name=f'pysdktest-my-resources-{suffix}', values=[{'name': 'v1', 'description': 'pysdktest'}]
        )
        cleanup.callback(access_broker.resources.labels.delete, label['keyId'])
        resource_type = access_broker.resources.types.create(name=f'pysdktest-my-resources-{suffix}')
        cleanup.callback(_delete_resource_type, access_broker, resource_type['resourceTypeId'])
        access_broker.resources.permissions.create(
            resource_type_id=resource_type['resourceTypeId'],
            name=f'pysdktest-my-resources-{suffix}',
            checkin_file=b'echo checkin',
            checkout_file=b'echo checkout',
        )
        resource = access_broker.resources.create(
            name=f'pysdktest-my-resources-{suffix}', resource_type_id=resource_type['resourceTypeId']
        )
        cleanup.callback(access_broker.resources.delete, resource['resourceId'])
        access_broker.resources.update(resource['resourceId'], resource_labels={label['keyName']: ['v1']})
        profile = access_broker.profiles.create(name=f'pysdktest-my-resources-{suffix}')
        cleanup.callback(access_broker.profiles.delete, profile['profileId'])
        access_broker.profiles.add_association(profile['profileId'], associations={label['keyName']: ['v1']})
        permission = next(
            p
            for p in access_broker.profiles.permissions.list_available_permissions(profile_id=profile['profileId'])
            if p['resourceTypeName'] == resource_type['name']
        )
        access_broker.profiles.permissions.add_permissions(
            profile_id=profile['profileId'],
            permission_id=permission['permissionId'],
            resource_type_id=resource_type['resourceTypeId'],
            version=1,
        )
        email = next(m for m in britive.global_settings.notification_mediums.list() if m['name'] == 'Email')
        condition = json.loads(
            britive.application_management.profiles.policies.build(
                name='approval', approval_notification_medium='Email', approver_users=[me['username']]
            )['condition']
        )
        condition['approval'].update(notificationMedium=[email['id']], approvers={'userIds': [me['userId']]})
        access_broker.profiles.policies.create(
            profile_id=profile['profileId'],
            name=f'pysdktest-my-resources-{suffix}',
            access_type='Allow',
            members={'users': [{'id': me['userId']}]},
            condition=condition,
        )
        yield {
            'me': me,
            'label': label['keyName'],
            'profile_id': profile['profileId'],
            'resource_id': resource['resourceId'],
        }


def _favorite_ids():
    return [f['favoriteId'] for f in britive.my_resources.favorites()]


@pytest.fixture
def favorite(resource_setup):
    created = britive.my_resources.add_favorite(
        resource_id=resource_setup['resource_id'], profile_id=resource_setup['profile_id']
    )
    yield created
    if created['favoriteId'] in _favorite_ids():
        britive.my_resources.delete_favorite(created['favoriteId'])


def test_list_resource_templates():
    assert isinstance(britive.my_resources.list_resource_templates()['templates'], list)


def test_list_resource_templates_search():
    assert britive.my_resources.list_resource_templates(search_text='no-such-template')['templates'] == []


def test_get_approvers(resource_setup):
    approvers = britive.my_resources.get_approvers(
        profile_id=resource_setup['profile_id'], resource_id=resource_setup['resource_id']
    )
    assert resource_setup['me']['userId'] in [u['id'] for u in approvers['approvers']['users']]


def test_get_resource_labels(resource_setup):
    labels = britive.my_approvals.get_resource_labels(resource_id=resource_setup['resource_id'])
    assert resource_setup['label'] in [label['name'] for label in labels['resourceLabels']]


def test_add_favorite(resource_setup, favorite):
    assert favorite['resourceId'] == resource_setup['resource_id']
    assert favorite['profileId'] == resource_setup['profile_id']
    assert favorite['favoriteId'] in _favorite_ids()


def test_delete_favorite(resource_setup, favorite):
    assert britive.my_resources.delete_favorite(favorite_id=favorite['favoriteId']) is None
    assert favorite['favoriteId'] not in _favorite_ids()


@pytest.mark.skip(reason='checkout variables need a resource profile checked out through a running broker')
def test_checkout_variable_values():
    pass
