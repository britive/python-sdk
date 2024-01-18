from .cache import *  # will also import some globals like `britive`


tag_keys = [
    'userTagId',
    'status',
    'description',
    'name',
    'external',
    'userCount',
    'userTagIdentityProviders'
]


def test_create(cached_tag):
    assert isinstance(cached_tag, dict)
    assert set(tag_keys).issubset(cached_tag.keys())


def test_get(cached_tag):
    tag = britive.tags.get(cached_tag['userTagId'])
    assert isinstance(tag, dict)
    assert set(tag_keys).issubset(tag.keys())


def test_list(cached_tag):
    tags = britive.tags.list()
    assert isinstance(tags, list)
    assert isinstance(tags[0], dict)
    assert cached_tag['name'] in [t['name'] for t in tags]


def test_search(cached_tag):
    tags = britive.tags.search(cached_tag['name'])
    assert isinstance(tags, list)
    assert isinstance(tags[0], dict)
    assert cached_tag['name'] == tags[0]['name']


def test_users_for_tag_zero(cached_tag):
    users = britive.tags.users_for_tag(tag_id=cached_tag['userTagId'])
    assert isinstance(users, list)
    assert len(users) == 0


def test_available_users_for_tag(cached_tag):
    users = britive.tags.available_users_for_tag(tag_id=cached_tag['userTagId'])
    assert isinstance(users, list)
    assert len(users) > 0
    assert isinstance(users[0], dict)


def test_add_user(cached_tag, cached_user):
    user_added = britive.tags.add_user(tag_id=cached_tag['userTagId'], user_id=cached_user['userId'])
    assert isinstance(user_added, dict)


def test_users_for_tag_one(cached_tag):
    users = britive.tags.users_for_tag(tag_id=cached_tag['userTagId'])
    assert isinstance(users, list)
    assert len(users) == 1
    assert isinstance(users[0], dict)


def test_remove_user(cached_tag, cached_user):
    response = britive.tags.remove_user(tag_id=cached_tag['userTagId'], user_id=cached_user['userId'])
    assert response is None


def test_enable(cached_tag):
    response = britive.tags.enable(cached_tag['userTagId'])
    assert isinstance(response, dict)
    assert response['userTagId'] == cached_tag['userTagId']
    assert response['status'] == 'Active'


def test_disable(cached_tag):
    response = britive.tags.disable(cached_tag['userTagId'])
    assert isinstance(response, dict)
    assert response['userTagId'] == cached_tag['userTagId']
    assert response['status'] == 'Inactive'


def test_update(cached_tag):
    r = str(random.randint(0, 1000000))
    tag = britive.tags.update(cached_tag['userTagId'], name=f'testpythonapteiwrappertag-{r}')
    assert isinstance(tag, dict)
    assert set(tag_keys).issubset(tag.keys())
    assert tag['name'] == f'testpythonapteiwrappertag-{r}'
    # set it back for downstream processes
    britive.tags.update(cached_tag['userTagId'], name=cached_tag['name'])


def test_membership_rules_list(cached_tag):
    response = britive.tags.membership_rules.list(tag_id=cached_tag['userTagId'])
    assert len(response) == 0


def test_membership_rules_create(cached_tag, cached_user):
    rules = [
        britive.tags.membership_rules.build(attribute_id_or_name='Email', operator='is', value=cached_user['email'])
    ]

    response = britive.tags.membership_rules.create(tag_id=cached_tag['userTagId'], rules=rules)
    assert len(response) == 1

    response = britive.tags.membership_rules.list(tag_id=cached_tag['userTagId'])
    assert len(response) == 1


def test_membership_rules_update(cached_tag, cached_user):
    rules = [
        britive.tags.membership_rules.build(
            attribute_id_or_name='Email',
            operator='is',
            value=cached_user['email']
        ),
        britive.tags.membership_rules.build(
            attribute_id_or_name='Username',
            operator='is',
            value=cached_user['username']
        )
    ]

    response = britive.tags.membership_rules.update(tag_id=cached_tag['userTagId'], rules=rules)
    assert response is None

    response = britive.tags.membership_rules.list(tag_id=cached_tag['userTagId'])
    assert len(response) == 2


def test_membership_rules_matched_users(cached_tag, cached_user):
    response = britive.tags.membership_rules.matched_users(tag_id=cached_tag['userTagId'])
    assert len(response) == 1
    assert response[0]['email'] == cached_user['email']


def test_membership_rules_delete(cached_tag):
    response = britive.tags.membership_rules.delete(tag_id=cached_tag['userTagId'])
    assert response is None

    response = britive.tags.membership_rules.list(tag_id=cached_tag['userTagId'])
    assert len(response) == 0


def test_minimized_user_details(cached_tag):
    details = britive.tags.minimized_tag_details(tag_id=cached_tag['userTagId'])
    assert isinstance(details, list)
    assert len(details) == 1
    details = britive.tags.minimized_tag_details(tag_ids=[cached_tag['userTagId']])
    assert isinstance(details, list)
    assert len(details) == 1
