from .cache import *  # will also import some globals like `britive`


def test_list():
    secrets = britive.my_secrets.list()
    assert isinstance(secrets, list)
    assert len(secrets) > 0
    assert isinstance(secrets[0], dict)


def test_view_no_approval(cached_secret):
    data = britive.my_secrets.view(path=cached_secret['path'])
    assert isinstance(data, dict)
