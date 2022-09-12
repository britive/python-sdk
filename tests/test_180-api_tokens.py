from .cache import *  # will also import some globals like `britive`


def test_create(cached_api_token):
    assert isinstance(cached_api_token, dict)
    assert 'token' in cached_api_token.keys()


def test_list(cached_api_token):
    tokens = britive.api_tokens.list()
    assert isinstance(tokens, list)
    assert cached_api_token['id'] in [t['id'] for t in tokens]


def test_get(cached_api_token):
    token = britive.api_tokens.get(token_id=cached_api_token['id'])
    assert isinstance(token, dict)
    assert token['id'] == cached_api_token['id']


def test_update(cached_api_token):
    r = str(random.randint(0, 1000000))
    new_name = f'test-{r}'
    response = britive.api_tokens.update(token_id=cached_api_token['id'], name=new_name)
    assert response is None
    response = britive.api_tokens.update(token_id=cached_api_token['id'], expiration_days=10)
    assert response is None
    token = britive.api_tokens.get(token_id=cached_api_token['id'])
    assert token['tokenExpirationDays'] == 10
    assert token['name'] == new_name


def test_delete(cached_api_token):
    response = britive.api_tokens.delete(token_id=cached_api_token['id'])
    assert response is None
    cleanup('api-token')
