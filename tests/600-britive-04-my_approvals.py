from .cache import *  # will also import some globals like `britive`


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_approval(cached_profile_checkout_request):
    request_id = request['requestId']

    response = britive.my_access.reject_request(request_id=request_id)

    assert response is None

    approvals = britive.my_access.list_approvals()
    for approval in approvals:
        if approval['requestId'] == request_id:
            assert approval['status'] == 'REJECTED'
            break
