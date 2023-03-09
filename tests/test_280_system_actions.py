from .cache import *  # will also import some globals like `britive`


def test_list():
    response1 = britive.system.actions.list()
    assert isinstance(response1, list)
    assert len(response1) > 0
    assert isinstance(response1[0], dict)
    assert 'name' in response1[0].keys()
    assert 'tenantId' in response1[0].keys()

    response2 = britive.system.actions.list(consumer='apps')
    assert isinstance(response2, list)
    assert len(response2) > 0
    assert isinstance(response2[0], dict)
    assert 'name' in response2[0].keys()
    assert 'tenantId' in response2[0].keys()

    assert len(response2) < len(response1)

    consumers = list(set([c['consumer'] for c in response2]))

    assert len(consumers) == 1
    assert consumers[0] == 'apps'

