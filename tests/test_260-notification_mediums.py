from .cache import * # will also import some globals like `britive`


def test_create(cached_notification_medium):
    assert isinstance(cached_notification_medium, dict)
    assert cached_notification_medium['name'] == 'pytest-notification-medium'

def test_list():
    response = britive.notification_mediums.list()
    assert isinstance(response, list)
    assert isinstance(response[0], dict)

def test_get(cached_notification_medium):
    response = britive.notification_mediums.get(cached_notification_medium['id'])
    assert isinstance(response, dict)
    assert response['name'] == 'pytest-notification-medium'

def test_update(cached_notification_medium):
    britive.notification_mediums.update(
        cached_notification_medium['id'],
        parameters={'name' : 'pytest-notification-medium-u'}
    )
    response = britive.notification_mediums.get(cached_notification_medium['id'])
    assert response['name'] == 'pytest-notification-medium-u'
