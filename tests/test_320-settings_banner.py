import datetime
from .cache import *  # will also import some globals like `britive`


def test_get():
    banner = britive.settings.banner.get()
    assert isinstance(banner, dict)


def test_set_no_schedule():
    banner = britive.settings.banner.set(message='test', display_banner=True, message_type='INFO')
    assert isinstance(banner, dict)
    for key in ['status', 'messageType', 'message']:
        assert key in banner
    assert 'messageSchedule' not in banner


def test_set_with_schedule():
    start_datetime = datetime.datetime.today()
    banner = britive.settings.banner.set(
        message='test',
        display_banner=True,
        message_type='INFO',
        start_datetime=start_datetime,
        end_datetime=start_datetime + datetime.timedelta(days=1),
        time_zone='UTC'
    )
    assert isinstance(banner, dict)
    for key in ['status', 'messageType', 'message', 'messageSchedule']:
        assert key in banner
    for key in ['startDate', 'endDate', 'timeZone']:
        assert key in banner['messageSchedule']


def test_set_with_incorrect_schedule():
    with pytest.raises(ValueError):
        britive.settings.banner.set(
            message='test',
            display_banner=True,
            message_type='INFO',
            start_datetime=datetime.datetime(year=2024, month=1, day=1),
            time_zone='UTC'
        )

    with pytest.raises(ValueError):
        britive.settings.banner.set(
            message='test',
            display_banner=True,
            message_type='INFO',
            end_datetime=datetime.datetime(year=2024, month=1, day=1),
            time_zone='UTC'
        )

    with pytest.raises(ValueError):
        britive.settings.banner.set(
            message='test',
            display_banner=True,
            message_type='INFO',
            start_datetime=datetime.datetime(year=2024, month=1, day=1),
            end_datetime=datetime.datetime(year=2024, month=1, day=1)
        )

    with pytest.raises(ValueError):
        britive.settings.banner.set(
            message='test',
            display_banner=True,
            message_type='INFO',
            start_datetime=datetime.datetime(year=2024, month=1, day=1)
        )

    with pytest.raises(ValueError):
        britive.settings.banner.set(
            message='test',
            display_banner=True,
            message_type='INFO',
            end_datetime=datetime.datetime(year=2024, month=1, day=1)
        )

    with pytest.raises(ValueError):
        britive.settings.banner.set(
            message='test',
            display_banner=True,
            message_type='INFO',
            time_zone='UTC'
        )


def test_banner_end_user():
    banner = britive.banner()
    assert isinstance(banner, dict)
    assert 'message' in banner
    assert 'messageType' in banner


def test_banner_off():
    banner = britive.settings.banner.set(display_banner=False, message='dont care', message_type='INFO')
    assert 'status' in banner
    assert banner['status'] == 'OFF'
    banner = britive.banner()
    assert banner is None
