from .cache import *  # will also import some globals like `britive`

# The calling identity is made an owner of a throwaway tag, so every call below runs as a tag owner. The tag and the
# user added to it are deleted at the end of the module, even if a test fails.


@pytest.fixture(scope='module')
def owned_tag():
    me = britive.my_access.whoami()
    suffix = int(time())
    tag = britive.identity_management.tags.create(
        name=f'pysdktest-managed-tag-{suffix}', description='my_managed_tags live test'
    )
    user = None
    try:
        # owners are set through the admin tag update; the SDK has no method for it
        britive.patch(
            f'{britive.base_url}/user-tags',
            json={
                'userTagId': tag['userTagId'],
                'name': tag['name'],
                'description': tag['description'],
                'relationships': {'owners': [{'relatedEntityId': me['userId'], 'relatedEntityType': 'User'}]},
            },
        )
        user = britive.identity_management.users.create(
            username=f'pysdktest-managed-tag-member-{suffix}',
            email=f'pysdktest.managed-tag-member.{suffix}@britive.com',
            firstName='TestPython',
            lastName=str(suffix),
            password=generate_random_password(),
            status='active',
        )
        yield {'tag': tag, 'user': user, 'state': {}}
    finally:
        britive.identity_management.tags.delete(tag['userTagId'])
        if user:
            britive.identity_management.users.delete(user['userId'])


def _users(result):
    return result.get('users', []) if isinstance(result, dict) else result


def _string_attribute():
    attributes = britive.my_managed_tags.list_identity_attributes()
    return next(a for a in attributes if a.get('dataType') == 'String' and not a.get('multiValued'))


def test_list():
    tags = britive.my_managed_tags.list()
    assert isinstance(tags, (dict, list))


def test_list_search():
    tags = britive.my_managed_tags.list(search_text='no-such-tag', page=0, size=20)
    assert isinstance(tags, (dict, list))


def test_list_finds_owned_tag(owned_tag):
    tags = britive.my_managed_tags.list(search_text=owned_tag['tag']['name'])
    tags = tags.get('userTags', []) if isinstance(tags, dict) else tags
    assert owned_tag['tag']['userTagId'] in [t['userTagId'] for t in tags]


def test_list_members_starts_empty(owned_tag):
    assert _users(britive.my_managed_tags.list_members(owned_tag['tag']['userTagId'])) == []


def test_list_available_members(owned_tag):
    available = britive.my_managed_tags.list_available_members(
        owned_tag['tag']['userTagId'], search_text=owned_tag['user']['username']
    )
    assert owned_tag['user']['userId'] in [u['userId'] for u in _users(available)]


def test_add_member(owned_tag):
    tag_id, user_id = owned_tag['tag']['userTagId'], owned_tag['user']['userId']
    response = britive.my_managed_tags.add_member(tag_id, user_id)
    assert response['userId'] == user_id
    assert user_id in [u['userId'] for u in _users(britive.my_managed_tags.list_members(tag_id))]


def test_list_members_search(owned_tag):
    members = britive.my_managed_tags.list_members(
        owned_tag['tag']['userTagId'], search_text=owned_tag['user']['username']
    )
    assert owned_tag['user']['userId'] in [u['userId'] for u in _users(members)]


def test_remove_member(owned_tag):
    tag_id, user_id = owned_tag['tag']['userTagId'], owned_tag['user']['userId']
    assert britive.my_managed_tags.remove_member(tag_id, user_id) is None
    assert user_id not in [u['userId'] for u in _users(britive.my_managed_tags.list_members(tag_id))]


def test_list_identity_attributes():
    attributes = britive.my_managed_tags.list_identity_attributes()
    assert isinstance(attributes, list)
    assert all('id' in a and 'name' in a for a in attributes)


def test_add_attribute_criteria(owned_tag):
    tag_id = owned_tag['tag']['userTagId']
    attribute = _string_attribute()
    assert britive.my_managed_tags.get_attribute_criteria(tag_id) == []

    added = britive.my_managed_tags.add_attribute_criteria(
        tag_id, [{'attributeId': attribute['id'], 'operator': 'is', 'value': 'pysdktest-a'}]
    )
    assert len(added) == 1
    assert added[0]['attributeId'] == attribute['id']
    assert added[0]['value'] == 'pysdktest-a'
    assert britive.my_managed_tags.get_attribute_criteria(tag_id) == added
    owned_tag['state']['criterion'] = added[0]


def test_update_attribute_criteria(owned_tag):
    tag_id = owned_tag['tag']['userTagId']
    criterion = owned_tag['state']['criterion']
    updated = {**criterion, 'operator': 'contains', 'value': 'pysdktest-b'}

    assert britive.my_managed_tags.update_attribute_criteria(tag_id, [updated]) is None
    assert britive.my_managed_tags.get_attribute_criteria(tag_id) == [updated]


def test_list_matched_members(owned_tag):
    matched = britive.my_managed_tags.list_matched_members(owned_tag['tag']['userTagId'], search_text='pysdktest')
    assert isinstance(_users(matched), list)


def test_clear_attribute_criteria(owned_tag):
    tag_id = owned_tag['tag']['userTagId']
    assert britive.my_managed_tags.update_attribute_criteria(tag_id, []) is None
    assert britive.my_managed_tags.get_attribute_criteria(tag_id) == []


def test_list_requested_memberships(owned_tag):
    requested = britive.my_managed_tags.list_requested_memberships(owned_tag['tag']['userTagId'])
    assert _users(requested) == []


@pytest.mark.skip(reason='needs a membership granted through a tag access request')
def test_remove_requested_membership():
    pass


@pytest.mark.parametrize('grant_type', ['app-profiles', 'resources', 'secrets'])
def test_list_tag_request_grants(owned_tag, grant_type):
    grants = britive.my_approvals.list_tag_request_grants(tag_id=owned_tag['tag']['userTagId'], grant_type=grant_type)
    assert isinstance(grants, (dict, list))
