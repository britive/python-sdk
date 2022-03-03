from .cache import *  # will also import some globals like `britive`

user_keys = [
    'userId',
    'status',
    'external',
    'mappedAccounts',
    'identityProvider',
    'mobile',
    'externalId',
    'name',
    'firstName',
    'lastName',
    'username',
    'email',
    'type',
    'adminRoles'
]


def test_create(cached_user):
    assert isinstance(cached_user, dict)
    assert set(user_keys).issubset(cached_user.keys())


def test_list(cached_user):
    response = britive.users.list()
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert set(user_keys).issubset(response[0].keys())
    assert cached_user['userId'] in [x['userId'] for x in response]


def test_get(cached_user):
    user = britive.users.get(cached_user['userId'])
    assert isinstance(user, dict)
    assert set(user_keys).issubset(user.keys())
    assert user['userId'] == cached_user['userId']


def test_get_by_name_co(cached_user):
    users = britive.users.get_by_name(cached_user['lastName'])
    assert isinstance(users, list)
    assert isinstance(users[0], dict)
    assert set(user_keys).issubset(users[0].keys())


def test_search(cached_user):
    users = britive.users.search(cached_user['email'].split('@')[0])
    assert isinstance(users, list)
    assert len(users) > 0
    assert isinstance(users[0], dict)
    assert set(user_keys).issubset(users[0].keys())


def test_get_by_status():
    users = britive.users.get_by_status('active')
    assert isinstance(users, list)
    assert len(users) > 0
    assert isinstance(users[0], dict)
    assert set(user_keys).issubset(users[0].keys())


def test_update(cached_user):
    user = britive.users.update(cached_user['userId'], mobile='1234567890')
    assert isinstance(user, dict)
    assert user['mobile'] == '1234567890'


def test_disable_single(cached_user):
    user = britive.users.disable(user_id=cached_user['userId'])
    assert isinstance(user, dict)
    assert user['status'] == 'inactive'


def test_enable_single(cached_user):
    user = britive.users.enable(user_id=cached_user['userId'])
    assert isinstance(user, dict)
    assert user['status'] == 'active'


def test_disable_list(cached_user):
    user = britive.users.disable(user_id=cached_user['userId'], user_ids=[cached_user['userId']])
    assert isinstance(user, list)
    assert user[0]['status'] == 'inactive'


def test_enable_list(cached_user):
    user = britive.users.enable(user_id=cached_user['userId'], user_ids=[cached_user['userId']])
    assert isinstance(user, list)
    assert user[0]['status'] == 'active'


def test_reset_password(cached_user):
    response = britive.users.reset_password(cached_user['userId'], generate_random_password())
    assert response is None


def test_reset_mfa(cached_user):
    with pytest.raises(exceptions.UserDoesNotHaveMFAEnabled):
        britive.users.reset_mfa(cached_user['userId'])





