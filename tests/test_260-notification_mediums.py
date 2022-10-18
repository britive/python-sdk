from .cache import *  # will also import some globals like `britive`


def test_create(cached_notification_medium):
    assert isinstance(cached_notification_medium, dict)
    assert 'pytest-nm-' in cached_notification_medium['name']


def test_list():
    response = britive.notification_mediums.list()
    assert isinstance(response, list)
    assert isinstance(response[0], dict)


def test_get(cached_notification_medium):
    response = britive.notification_mediums.get(cached_notification_medium['id'])
    assert isinstance(response, dict)
    assert response['name'] == cached_notification_medium['name']


def test_update(cached_notification_medium):
    r = str(random.randint(0, 1000000))
    new_name = f'pytest-nm-{r}'
    britive.notification_mediums.update(
        cached_notification_medium['id'],
        parameters={'name': new_name}
    )
    response = britive.notification_mediums.get(cached_notification_medium['id'])
    assert response['name'] == new_name
