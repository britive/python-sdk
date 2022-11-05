from .cache import * # will also import some globals like `britive`

def test_get(cached_approval):
    response = britive.approvals.get(cached_approval['requestId'])
    assert isinstance(response, dict)
    assert "requestId" in response.keys()

def test_list():
    response = britive.approvals.list()
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    
def test_review(cached_approval):
    britive.approvals.review(True, cached_approval['requestId'])
    #make sure the string 'ACCEPTED' is accurate
    assert britive.approvals.get(cached_approval['requestId'])['status'] == 'ACCEPTED'

