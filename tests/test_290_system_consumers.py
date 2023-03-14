from .cache import *  # will also import some globals like `britive`


def test_list():
    response = britive.system.consumers.list()
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert 'name' in response[0].keys()

