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


def test_frequents():
    profiles = britive.my_access.frequents()
    assert isinstance(profiles, list)


def test_favorites():
    profiles = britive.my_access.favorites()
    assert isinstance(profiles, list)
