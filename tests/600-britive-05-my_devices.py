from contextlib import ExitStack

from britive.exceptions.generic import BritiveGenericError

from .cache import *  # will also import some globals like `britive`

# The configured app/device must be a test fixture. The temporary profile has no grant/revoke scripts, so its
# checkout is refused. Tests that actually execute scripts remain skipped and require a disposable device.
device_app_id = os.getenv('BRITIVE_TEST_DEVICE_APP_ID')
device_hostname = os.getenv('BRITIVE_TEST_DEVICE_HOSTNAME')
device_skip = not (device_app_id and device_hostname)
device_skip_message = 'BRITIVE_TEST_DEVICE_APP_ID and/or BRITIVE_TEST_DEVICE_HOSTNAME not set'
scripts_skip_message = 'checking out runs grant/revoke scripts on a device; requires a disposable device'
pytestmark = pytest.mark.skipif(device_skip, reason=device_skip_message)


def _find_device(devices_url):
    page = 0
    while True:
        devices = britive.get(devices_url, params={'page': page, 'size': 100}, pagination='none')
        for device in devices['data']:
            if device['hostname'] == device_hostname:
                return device
        if not devices['data'] or (page + 1) * 100 >= devices['count']:
            pytest.skip(f'device {device_hostname} not found in application {device_app_id}')
        page += 1


@pytest.fixture(scope='module')
def device_setup():
    me = britive.my_access.whoami()
    suffix = int(time() * 1_000_000)
    environment = britive.application_management.environments.list(device_app_id)[0]
    devices_url = (
        f'{britive.base_url}/apps/{device_app_id}/environments/'
        f'{environment.get("id") or environment["environmentId"]}/devices'
    )
    device = _find_device(devices_url)
    users_url = f'{devices_url}/{device["deviceId"]}/users'
    profiles = britive.application_management.profiles
    with ExitStack() as cleanup:
        if me['userId'] not in [u['userId'] for u in britive.get(users_url)]:
            britive.post(users_url, json=[me['userId']])
            cleanup.callback(britive.delete, f'{users_url}/{me["userId"]}')
        profile = profiles.create(application_id=device_app_id, name=f'pysdktest-devices-{suffix}')
        cleanup.callback(profiles.delete, device_app_id, profile['papId'])
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


def _device_profile(profile_id):
    page = 0
    while True:
        devices = britive.my_devices.list(page=page, size=100)
        for device in devices['data']:
            if device['papId'] == profile_id:
                return device
        if not devices['data'] or (page + 1) * 100 >= devices['count']:
            raise AssertionError(f'Test device profile {profile_id} was not listed.')
        page += 1


def test_list():
    assert isinstance(britive.my_devices.list()['data'], list)


def test_list_search():
    assert britive.my_devices.list(search_text='no-such-device', page=0, size=20)['data'] == []


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
    request_id = request['requestId']
    try:
        assert britive.my_requests.approval_request_status(request_id=request_id)['status'] == 'PENDING'
    finally:
        britive.my_devices.withdraw_approval_request(profile_id=device['papId'], device_id=device['deviceId'])
    assert britive.my_requests.approval_request_status(request_id=request_id)['status'].upper() == 'WITHDRAWN'


@pytest.mark.skip(reason=scripts_skip_message)
def test_checkout_needs_justification_for_approval():
    pass


@pytest.mark.skip(reason=scripts_skip_message)
def test_checkout_and_checkin():
    pass
