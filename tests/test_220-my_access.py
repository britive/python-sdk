from .cache import *  # will also import some globals like `britive`
import json


def test_whoami():
    me = britive.my_access.whoami()
    assert isinstance(me, dict)
    print(json.dumps(me, indent=2, default=str))


def test_list_profiles():
    profiles = britive.my_access.list_profiles()
    assert isinstance(profiles, list)
    assert len(profiles) > 0
    assert isinstance(profiles[0], dict)


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_checkout(cached_checked_out_profile):
    assert isinstance(cached_checked_out_profile, dict)
    assert cached_checked_out_profile['accessType'] == 'PROGRAMMATIC'
    assert 'credentials' in cached_checked_out_profile.keys()


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_checkout_again(cached_profile, cached_environment):
    response = britive.my_access.checkout(
            profile_id=cached_profile['papId'],
            environment_id=cached_environment['id'],
            include_credentials=True
        )

    assert isinstance(response, dict)
    assert response['accessType'] == 'PROGRAMMATIC'
    assert 'credentials' in response.keys()


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_list_checked_out_profiles():
    profiles = britive.my_access.list_checked_out_profiles()
    assert isinstance(profiles, list)
    assert len(profiles) >= 1  # since we just checked one out!


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_get_checked_out_profile(cached_checked_out_profile):
    profile = britive.my_access.get_checked_out_profile(transaction_id=cached_checked_out_profile['transactionId'])
    assert isinstance(profile, dict)


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_checkin(cached_checked_out_profile):
    response = britive.my_access.checkin(transaction_id=cached_checked_out_profile['transactionId'])
    assert isinstance(response, dict)
    assert response['status'] in ('checkedIn', 'checkInSubmitted')  # v1, v2
    cleanup('checked-out-profile')


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_checkout_by_name(cached_checked_out_profile_by_name):
    assert isinstance(cached_checked_out_profile_by_name, dict)
    assert cached_checked_out_profile_by_name['accessType'] == 'PROGRAMMATIC'
    assert 'credentials' in cached_checked_out_profile_by_name.keys()


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_checkin_by_name(cached_profile, cached_environment, cached_application):
    account_id = os.environ['BRITIVE_TEST_ENV_ACCOUNT_ID']
    response = britive.my_access.checkin_by_name(
        profile_name=cached_profile['name'],
        environment_name=f'{account_id} ({cached_environment["name"]})',
        application_name=cached_application['catalogAppDisplayName']
    )
    assert isinstance(response, dict)
    assert response['status'] in ('checkedIn', 'checkInSubmitted')  # v1, v2
    cleanup('checked-out-profile-by-name')


def test_frequents():
    profiles = britive.my_access.frequents()
    assert isinstance(profiles, list)


def test_favorites():
    profiles = britive.my_access.favorites()
    assert isinstance(profiles, list)


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_request_and_approve(cached_profile, cached_service_identity_token, cached_environment,
                             cached_service_identity):

    token = britive.service_identity_tokens.create(cached_service_identity['userId'], 90)['token']
    other_britive = Britive(token=token, query_features=False)

    request = other_britive.my_access.request_approval(
        profile_id=cached_profile['papId'],
        environment_id=cached_environment['id'],
        justification='let me in'
    )

    assert 'requestId' in request.keys()

    request_id = request['requestId']

    approvals = britive.my_access.list_approvals()
    for approval in approvals:
        if approval['requestId'] == request_id:
            assert approval['status'] == 'PENDING'
            break

    response = britive.my_access.reject_request(
        request_id=request_id
    )

    assert response is None

    approvals = britive.my_access.list_approvals()
    for approval in approvals:
        if approval['requestId'] == request_id:
            assert approval['status'] == 'REJECTED'
            break

    request = other_britive.my_access.request_approval(
        profile_id=cached_profile['papId'],
        environment_id=cached_environment['id'],
        justification='let me in'
    )

    assert 'requestId' in request.keys()

    request_id = request['requestId']

    approvals = britive.my_access.list_approvals()
    for approval in approvals:
        if approval['requestId'] == request_id:
            assert approval['status'] == 'PENDING'
            break

    response = britive.my_access.approve_request(
        request_id=request_id
    )

    assert response is None

    approvals = britive.my_access.list_approvals()
    for approval in approvals:
        if approval['requestId'] == request_id:
            assert approval['status'] == 'APPROVED'
            break

