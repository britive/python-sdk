from .cache import *  # will also import some globals like `britive`


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_request(cached_profile_checkout_request):
    assert 'requestId' in cached_profile_checkout_request

    request_id = request['requestId']

    approvals = britive.my_requests.list()
    for approval in approvals:
        if approval['requestId'] == request_id:
            assert approval['status'] == 'PENDING'
            break
