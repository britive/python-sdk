from .cache import *  # will also import some globals like `britive`


def test_service_identity_tokens_create(cached_service_identity_token):
    assert isinstance(cached_service_identity_token, dict)
    assert cached_service_identity_token['tokenExpirationDays'] == 90
    assert 'token' in cached_service_identity_token.keys()


def test_service_identity_tokens_update(cached_service_identity):
    token = britive.service_identity_tokens.update(cached_service_identity['userId'], token_expiration_days=45)
    assert isinstance(token, dict)
    assert token['tokenExpirationDays'] == 45
    assert 'token' in token.keys()


def test_service_identity_tokens_get(cached_service_identity):
    token = britive.service_identity_tokens.get(cached_service_identity['userId'])
    assert isinstance(token, dict)
    assert token['tokenExpirationDays'] == 45
    assert 'token' in token.keys()




