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


def test_checkout(cached_checked_out_profile):
    assert isinstance(cached_checked_out_profile, dict)
    assert cached_checked_out_profile['accessType'] == 'PROGRAMMATIC'
    assert 'credentials' in cached_checked_out_profile.keys()


def test_list_checked_out_profiles():
    profiles = britive.my_access.list_checked_out_profiles()
    assert isinstance(profiles, list)
    assert len(profiles) >= 1  # since we just checked one out!


def test_checkin(cached_checked_out_profile):
    response = britive.my_access.checkin(transaction_id=cached_checked_out_profile['transactionId'])
    assert isinstance(response, dict)
    assert response['status'] == 'checkedIn'
    cleanup('checked-out-profile')


def test_checkout_by_name(cached_checked_out_profile_by_name):
    assert isinstance(cached_checked_out_profile_by_name, dict)
    assert cached_checked_out_profile_by_name['accessType'] == 'PROGRAMMATIC'
    assert 'credentials' in cached_checked_out_profile_by_name.keys()


def test_checkin_by_name(cached_profile, cached_environment):
    account_id = os.environ['BRITIVE_TEST_ENV_ACCOUNT_ID']
    response = britive.my_access.checkin_by_name(
        profile_name=cached_profile['name'],
        environment_name=f'{account_id} ({cached_environment["name"]})'
    )
    assert isinstance(response, dict)
    assert response['status'] == 'checkedIn'
    cleanup('checked-out-profile-by-name')


def test_frequents():
    profiles = britive.my_access.frequents()
    assert isinstance(profiles, list)


def test_favorites():
    profiles = britive.my_access.favorites()
    assert isinstance(profiles, list)
