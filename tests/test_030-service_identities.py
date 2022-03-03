from .cache import *  # will also import some globals like `britive`


service_identity_keys = [
    'userId',
    'status',
    'description',
    'name',
    'type',
    'adminRoles'
]


def test_create(cached_service_identity):
    assert isinstance(cached_service_identity, dict)
    assert set(service_identity_keys).issubset(cached_service_identity.keys())


def test_list(cached_service_identity):
    response = britive.service_identities.list()
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert set(service_identity_keys).issubset(response[0].keys())
    assert cached_service_identity['userId'] in [x['userId'] for x in response]


def test_get(cached_service_identity):
    user = britive.service_identities.get(cached_service_identity['userId'])
    assert isinstance(user, dict)
    assert set(service_identity_keys).issubset(user.keys())


def test_get_by_name_co(cached_service_identity):
    users = britive.service_identities.get_by_name(cached_service_identity['name'])
    assert isinstance(users, list)
    assert isinstance(users[0], dict)
    assert set(service_identity_keys).issubset(users[0].keys())


def test_search(cached_service_identity):
    users = britive.service_identities.search(cached_service_identity['name'].split('@')[0])
    assert isinstance(users, list)
    assert len(users) > 0
    assert isinstance(users[0], dict)
    assert set(service_identity_keys).issubset(users[0].keys())


def test_get_by_status():
    users = britive.service_identities.get_by_status('active')
    assert isinstance(users, list)
    assert len(users) > 0
    assert isinstance(users[0], dict)
    assert set(service_identity_keys).issubset(users[0].keys())


def test_update(cached_service_identity):
    user = britive.service_identities.update(cached_service_identity['userId'], description='test2')
    assert isinstance(user, dict)
    assert user['description'] == 'test2'


def test_disable_single(cached_service_identity):
    user = britive.service_identities.disable(service_identity_id=cached_service_identity['userId'])
    assert isinstance(user, dict)
    assert user['status'] == 'inactive'


def test_enable_single(cached_service_identity):
    user = britive.service_identities.enable(service_identity_id=cached_service_identity['userId'])
    assert isinstance(user, dict)
    assert user['status'] == 'active'


def test_disable_list(cached_service_identity):
    user = britive.service_identities.disable(
        service_identity_id=cached_service_identity['userId'],
        service_identity_ids=[cached_service_identity['userId']]
    )
    assert isinstance(user, list)
    assert user[0]['status'] == 'inactive'


def test_enable_list(cached_service_identity):
    user = britive.service_identities.enable(
        service_identity_id=cached_service_identity['userId'],
        service_identity_ids=[cached_service_identity['userId']]
    )
    assert isinstance(user, list)
    assert user[0]['status'] == 'active'




