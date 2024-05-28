import pyotp
from .cache import *  # will also import some globals like `britive`

user_keys = {
    'adminRoles',
    'created',
    'email',
    'external',
    'externalId',
    'firstName',
    'identityProvider',
    'lastLogin',
    'lastName',
    'mappedAccounts',
    'mobile',
    'modified',
    'name',
    'phone',
    'status',
    'type',
    'userId',
    'userTags',
    'username'
}


def test_create(cached_user):
    assert isinstance(cached_user, dict)
    assert user_keys.issubset(cached_user)


def test_list(cached_user):
    response = britive.users.list()
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert user_keys.issubset(response[0])
    assert cached_user['userId'] in [x['userId'] for x in response]


def test_get(cached_user):
    user = britive.users.get(cached_user['userId'])
    assert isinstance(user, dict)
    assert user_keys.issubset(user)
    assert user['userId'] == cached_user['userId']


def test_get_by_name_co(cached_user):
    users = britive.users.get_by_name(cached_user['lastName'])
    assert isinstance(users, list)
    assert isinstance(users[0], dict)
    assert user_keys.issubset(users[0])


def test_search(cached_user):
    users = britive.users.search(cached_user['email'].split('@')[0])
    assert isinstance(users, list)
    assert len(users) > 0
    assert isinstance(users[0], dict)
    assert user_keys.issubset(users[0])


def test_get_by_status():
    users = britive.users.get_by_status('active')
    assert isinstance(users, list)
    assert len(users) > 0
    assert isinstance(users[0], dict)
    assert user_keys.issubset(users[0])


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


def test_set_custom_identity_attributes(cached_user, cached_identity_attribute):
    response = britive.service_identities.custom_attributes.add(
        principal_id=cached_user['userId'],
        custom_attributes={
            cached_identity_attribute['id']: [
                f'test-attr-value-{random.randint(0, 1000000)}'
            ]
        }
    )
    assert response is None


def test_get_custom_identity_attributes_list(cached_user, cached_identity_attribute):
    response = britive.service_identities.custom_attributes.get(
        principal_id=cached_user['userId'],
        as_dict=False
    )
    assert isinstance(response, list)
    assert len(response) == 1
    assert isinstance(response[0], dict)
    assert response[0]['attributeId'] == cached_identity_attribute['id']


def test_get_custom_identity_attributes_dict(cached_user, cached_identity_attribute):
    response = britive.service_identities.custom_attributes.get(
        principal_id=cached_user['userId'],
        as_dict=True
    )
    assert isinstance(response, dict)
    assert cached_identity_attribute['id'] in response
    assert response[cached_identity_attribute['id']].startswith('test-attr-value')


def test_remove_custom_identity_attributes(cached_user, cached_identity_attribute):
    value = britive.service_identities.custom_attributes.get(
        principal_id=cached_user['userId'],
        as_dict=True
    )[cached_identity_attribute['id']]
    response = britive.service_identities.custom_attributes.remove(
        principal_id=cached_user['userId'],
        custom_attributes={
            cached_identity_attribute['name']: [
                value
            ]
        }
    )
    assert response is None

    attributes = britive.service_identities.custom_attributes.get(
        principal_id=cached_user['userId'],
        as_dict=False
    )

    assert len(attributes) == 0


def test_minimized_user_details(cached_user):
    details = britive.users.minimized_user_details(user_id=cached_user['userId'])
    assert isinstance(details, list)
    assert len(details) == 1
    details = britive.users.minimized_user_details(user_ids=[cached_user['userId']])
    assert isinstance(details, list)
    assert len(details) == 1


def test_stepup_mfa():
    challenge = britive.users.enable_mfa.enable()
    totp = pyotp.TOTP(challenge.get('additionalDetails').get('key'))
    totp = totp.now()
    assert len(str(totp)) == 6
