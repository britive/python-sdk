from datetime import datetime, timezone

from britive.exceptions import BritiveException

from .cache import *  # will also import some globals like `britive`


@pytest.fixture(scope='module')
def temp_token():
    # Keep this short-lived credential in memory rather than the persistent pytest cache.
    token = britive.security.temp_tokens.create()
    yield token
    britive.security.temp_tokens.revoke(token=token['accessToken'])


@pytest.fixture(scope='module')
def temp_client(temp_token):
    client = Britive(tenant=britive.tenant, token=temp_token['accessToken'], query_features=False)
    yield client
    client.session.close()


def assert_token_details(token):
    assert isinstance(token, dict)
    assert isinstance(token['accessToken'], str)
    assert token['accessToken']
    assert isinstance(token['expiresOn'], str)
    expires_on = datetime.fromisoformat(token['expiresOn'].replace('Z', '+00:00'))
    assert expires_on > datetime.now(timezone.utc)


def test_create(temp_token):
    assert_token_details(temp_token)


def test_create_with_duration():
    token = britive.security.temp_tokens.create(duration_seconds=900)
    try:
        assert_token_details(token)
    finally:
        britive.security.temp_tokens.revoke(token=token['accessToken'])


def test_authenticate(temp_client):
    identity = temp_client.my_access.whoami()
    assert isinstance(identity, dict)
    assert identity['userId'] == britive.my_access.whoami()['userId']


def test_cannot_create_from_temp_token(temp_client):
    with pytest.raises(BritiveException, match=r'^403 - .*temporary token'):
        temp_client.security.temp_tokens.create()


@pytest.mark.parametrize('duration_seconds', [0, -1, 86401])
def test_invalid_duration(duration_seconds):
    with pytest.raises(BritiveException, match=r'^400 - '):
        britive.security.temp_tokens.create(duration_seconds=duration_seconds)


def test_revoke():
    token = britive.security.temp_tokens.create(duration_seconds=900)
    client = None
    revoked = False
    try:
        client = Britive(tenant=britive.tenant, token=token['accessToken'], query_features=False)
        identity = client.my_access.whoami()
        assert identity['userId'] == britive.my_access.whoami()['userId']
        headers = dict(britive.session.headers)

        response = britive.security.temp_tokens.revoke(token=token['accessToken'])
        revoked = True
        assert response is None
        assert dict(britive.session.headers) == headers
        with pytest.raises(BritiveException, match=r'^401 - '):
            client.my_access.whoami()
        assert britive.my_access.whoami()['userId'] == identity['userId']
    finally:
        if client is not None:
            client.session.close()
        if not revoked:
            britive.security.temp_tokens.revoke(token=token['accessToken'])
