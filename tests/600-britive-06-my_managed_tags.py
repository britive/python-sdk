from contextlib import ExitStack

from britive.exceptions import BritiveException

from .cache import *  # will also import some globals like `britive`


@pytest.fixture(scope='module')
def owned_tag():
    me = britive.my_access.whoami()
    suffix = int(time() * 1_000_000)
    with ExitStack() as cleanup:
        user = britive.identity_management.users.create(
            username=f'pysdktest-managed-tag-member-{suffix}',
            email=f'pysdktest.managed-tag-member.{suffix}@britive.com',
            firstName='TestPython',
            lastName=str(suffix),
            password=generate_random_password(),
            status='active',
        )
        cleanup.callback(britive.identity_management.users.delete, user['userId'])
        tag = britive.identity_management.tags.create(
            name=f'pysdktest-managed-tag-{suffix}', description='my_managed_tags live test'
        )
        cleanup.callback(britive.identity_management.tags.delete, tag['userTagId'])
        britive.patch(
            f'{britive.base_url}/user-tags',
            json={
                'userTagId': tag['userTagId'],
                'name': tag['name'],
                'description': tag['description'],
                'relationships': {'owners': [{'relatedEntityId': me['userId'], 'relatedEntityType': 'User'}]},
            },
        )
        yield {'tag': tag, 'user': user}


def _users(result):
    return result['data']


@pytest.fixture
def member(owned_tag):
    tag_id, user_id = owned_tag['tag']['userTagId'], owned_tag['user']['userId']
    added = britive.my_managed_tags.add_member(tag_id, user_id)
    yield added
    if user_id in [u['userId'] for u in _users(britive.my_managed_tags.list_members(tag_id))]:
        britive.my_managed_tags.remove_member(tag_id, user_id)


@pytest.fixture
def criterion(owned_tag):
    attributes = britive.my_managed_tags.list_identity_attributes()
    attribute = next(a for a in attributes if a.get('dataType') == 'String' and not a.get('multiValued'))
    tag_id = owned_tag['tag']['userTagId']
    added = britive.my_managed_tags.add_attribute_criteria(
        tag_id, [{'attributeId': attribute['id'], 'operator': 'is', 'value': 'pysdktest-a'}]
    )
    yield added[0]
    britive.my_managed_tags.update_attribute_criteria(tag_id, [])


def test_list():
    assert isinstance(britive.my_managed_tags.list()['data'], list)


def test_list_search():
    assert britive.my_managed_tags.list(search_text='no-such-tag', page=0, size=20)['data'] == []


def test_list_finds_owned_tag(owned_tag):
    tags = britive.my_managed_tags.list(search_text=owned_tag['tag']['name'])
    assert owned_tag['tag']['userTagId'] in [t['userTagId'] for t in tags['data']]


def test_list_paging(owned_tag):
    tags = britive.my_managed_tags.list(search_text=owned_tag['tag']['name'], page=0, size=1, sort='name,asc')
    assert tags['page'] == 0 and tags['size'] == 1
    assert [t['userTagId'] for t in tags['data']] == [owned_tag['tag']['userTagId']]


def test_list_members_starts_empty(owned_tag):
    assert _users(britive.my_managed_tags.list_members(owned_tag['tag']['userTagId'])) == []


def test_list_available_members(owned_tag):
    available = britive.my_managed_tags.list_available_members(
        owned_tag['tag']['userTagId'], search_text=owned_tag['user']['username']
    )
    assert owned_tag['user']['userId'] in [u['userId'] for u in _users(available)]


def test_add_member(owned_tag, member):
    assert member['userId'] == owned_tag['user']['userId']
    assert member['userId'] in [
        u['userId'] for u in _users(britive.my_managed_tags.list_members(owned_tag['tag']['userTagId']))
    ]


def test_list_members_search(owned_tag, member):
    members = britive.my_managed_tags.list_members(
        owned_tag['tag']['userTagId'], search_text=member['username'], page=0, size=20, sort='username,asc'
    )
    assert member['userId'] in [u['userId'] for u in _users(members)]


def test_remove_member(owned_tag, member):
    tag_id = owned_tag['tag']['userTagId']
    assert britive.my_managed_tags.remove_member(tag_id, member['userId']) is None
    assert member['userId'] not in [u['userId'] for u in _users(britive.my_managed_tags.list_members(tag_id))]


def test_list_identity_attributes():
    attributes = britive.my_managed_tags.list_identity_attributes()
    assert isinstance(attributes, list)
    assert all('id' in a and 'name' in a for a in attributes)


def test_add_attribute_criteria(owned_tag, criterion):
    assert criterion['value'] == 'pysdktest-a'
    assert britive.my_managed_tags.get_attribute_criteria(owned_tag['tag']['userTagId']) == [criterion]


def test_update_attribute_criteria(owned_tag, criterion):
    tag_id = owned_tag['tag']['userTagId']
    updated = {**criterion, 'operator': 'contains', 'value': 'pysdktest-b'}
    assert britive.my_managed_tags.update_attribute_criteria(tag_id, [updated]) is None
    assert britive.my_managed_tags.get_attribute_criteria(tag_id) == [updated]


def test_list_matched_members(owned_tag):
    matched = britive.my_managed_tags.list_matched_members(owned_tag['tag']['userTagId'], search_text='pysdktest')
    assert isinstance(_users(matched), list)


def test_clear_attribute_criteria(owned_tag, criterion):
    tag_id = owned_tag['tag']['userTagId']
    assert britive.my_managed_tags.update_attribute_criteria(tag_id, []) is None
    assert britive.my_managed_tags.get_attribute_criteria(tag_id) == []


def test_list_requested_memberships(owned_tag):
    assert _users(britive.my_managed_tags.list_requested_memberships(owned_tag['tag']['userTagId'])) == []


def test_non_owner_is_rejected():
    tag = britive.identity_management.tags.create(name=f'pysdktest-unowned-tag-{int(time() * 1_000_000)}')
    try:
        with pytest.raises(BritiveException, match=r'^403 - '):
            britive.my_managed_tags.list_members(tag['userTagId'])
    finally:
        britive.identity_management.tags.delete(tag['userTagId'])


@pytest.mark.skip(reason='needs a membership granted through a tag access request')
def test_remove_requested_membership():
    pass


@pytest.mark.parametrize('grant_type', ['app-profiles', 'resources', 'secrets'])
def test_list_tag_request_grants(owned_tag, grant_type):
    grants = britive.my_approvals.list_tag_request_grants(tag_id=owned_tag['tag']['userTagId'], grant_type=grant_type)
    assert isinstance(grants, list)
