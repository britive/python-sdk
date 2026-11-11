from britive.exceptions.generic import BritiveGenericError

from .cache import *  # will also import some globals like `britive`

# Devices come from an endpoint privilege management app (e.g. CrowdStrike Falcon) scanning real machines, so the tests
# need an existing app and device: set BRITIVE_TEST_DEVICE_APP_ID and BRITIVE_TEST_DEVICE_HOSTNAME. The calling identity
# is mapped to the device and given a throwaway device profile with no permissions (grant and revoke scripts), so
# nothing can run on the device: the API refuses to check it out. The profile and the mapping are removed at the end of
# the module, even if a test fails.

device_app_id = os.getenv('BRITIVE_TEST_DEVICE_APP_ID')
device_hostname = os.getenv('BRITIVE_TEST_DEVICE_HOSTNAME')
device_skip = not (device_app_id and device_hostname)
device_skip_message = 'BRITIVE_TEST_DEVICE_APP_ID and/or BRITIVE_TEST_DEVICE_HOSTNAME not set'
scripts_skip_message = 'checking out runs the profile grant and revoke scripts on the device, so needs a disposable one'


def _find_device(devices_url):
    page = 0
    while True:
        devices = britive.get(devices_url, params={'page': page, 'size': 100}, pagination='none')
        for device in devices['data']:
            if device['hostname'] == device_hostname:
                return device
        if (page + 1) * 100 >= devices['count']:
            pytest.skip(f'device {device_hostname} not found in application {device_app_id}')
        page += 1


@pytest.fixture(scope='module')
def device_setup():
    if device_skip:
        pytest.skip(device_skip_message)
    me = britive.my_access.whoami()
    suffix = int(time())
    environment = britive.application_management.environments.list(device_app_id)[0]
    devices_url = (
        f'{britive.base_url}/apps/{device_app_id}/environments/'
        f'{environment.get("id") or environment["environmentId"]}/devices'
    )
    device = _find_device(devices_url)
    users_url = f'{devices_url}/{device["deviceId"]}/users'
    profiles = britive.application_management.profiles
    mapped = profile = None
    try:
        if me['userId'] not in [u['userId'] for u in britive.get(users_url)]:
            britive.post(users_url, json=[me['userId']])
            mapped = True
        profile = profiles.create(application_id=device_app_id, name=f'pysdktest-devices-{suffix}')
        profiles.set_scopes(profile['papId'], [{'type': 'Platform', 'value': device['platformName'].lower()}])
        policy = profiles.policies.build(
            name=f'pysdktest-devices-{suffix}',
            users=[me['username']],
            approval_notification_medium='Email',
            approver_users=[me['username']],
        )
        profiles.policies.create(profile_id=profile['papId'], policy=policy)
        assert profiles.permissions.list_assigned(profile['papId']) == []
        yield {'profile_id': profile['papId'], 'hostname': device_hostname}
    finally:
        if profile:
            profiles.delete(device_app_id, profile['papId'])
        if mapped:
            britive.delete(f'{users_url}/{me["userId"]}')


def _device_profile(profile_id):
    devices = britive.my_devices.list()['data']
    return next(d for d in devices if d['papId'] == profile_id)


def test_list():
    devices = britive.my_devices.list()
    assert isinstance(devices['data'], list)


def test_list_search():
    devices = britive.my_devices.list(search_text='no-such-device', page=0, size=20)
    assert devices['data'] == []


def test_list_finds_device_profile(device_setup):
    device = _device_profile(device_setup['profile_id'])
    assert device['deviceName'] == device_setup['hostname']
    assert device['myAccessDetails']['status'] == 'ApprovalRequired'


def test_checkout_without_permissions_is_refused(device_setup):
    device = _device_profile(device_setup['profile_id'])
    with pytest.raises(BritiveGenericError, match='no permissions'):
        britive.my_devices.checkout(profile_id=device['papId'], device_id=device['deviceId'])


def test_request_and_withdraw_approval(device_setup):
    device = _device_profile(device_setup['profile_id'])
    request = britive.my_devices.request_approval(
        profile_id=device['papId'], device_id=device['deviceId'], justification='pysdktest'
    )
    assert request['requestId']
    assert britive.my_requests.approval_request_status(request_id=request['requestId'])['status'] == 'PENDING'

    response = britive.my_devices.withdraw_approval_request(profile_id=device['papId'], device_id=device['deviceId'])
    assert response is None
    status = britive.my_requests.approval_request_status(request_id=request['requestId'])['status']
    assert status.upper() == 'WITHDRAWN'


@pytest.mark.skip(reason=scripts_skip_message)
def test_checkout_needs_justification_for_approval():
    pass


@pytest.mark.skip(reason=scripts_skip_message)
def test_checkout_and_checkin():
    pass
