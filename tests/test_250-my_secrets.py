from .cache import *  # will also import some globals like `britive`

"""
---------NOTE---------

Since the admin API actions for Secrets Manager are not yet built into this Python API Wrapper then
some manual setup has to occur in the tenant used for testing. Specifically these tests will need at
least 1 secret available to the calling user/service identity and one of those secrets has to be named
"/Test".

This will change once the admin API actions are built into this package as we can then programmatically create
the vault and secrets before testing the britive.my_secrets functionality.
"""


def test_list():
    secrets = britive.my_secrets.list()
    assert isinstance(secrets, list)
    assert len(secrets) > 0
    assert isinstance(secrets[0], dict)


def test_view_no_approval(cached_secret):
    data = britive.my_secrets.view(path=cached_secret['path'])
    assert isinstance(data, dict)

