from .cache import *  # will also import some globals like `britive`


def test_create(cached_notification):
    assert isinstance(cached_notification, dict)
    assert cached_notification['description'] == 'test'


def test_list():
    notifications = britive.notifications.list()
    assert isinstance(notifications, list)
    assert len(notifications) > 0


def test_get(cached_notification):
    notification = britive.notifications.get(notification_id=cached_notification['notificationId'])
    assert isinstance(notification, dict)
    assert notification['notificationId'] == cached_notification['notificationId']


def test_update(cached_notification):
    notification = britive.notifications.update(
        notification_id=cached_notification['notificationId'],
        description='test2'
    )
    assert isinstance(notification, dict)
    assert notification['description'] == 'test2'


def test_disable(cached_notification):
    notification = britive.notifications.disable(notification_id=cached_notification['notificationId'])
    assert isinstance(notification, dict)
    assert notification['status'] == 'Inactive'


def test_enable(cached_notification):
    notification = britive.notifications.enable(notification_id=cached_notification['notificationId'])
    assert isinstance(notification, dict)
    assert notification['status'] == 'Active'


def test_available_rules(cached_notification_rules):
    assert isinstance(cached_notification_rules, list)


def test_available_users(cached_notification_users):
    assert isinstance(cached_notification_users, list)


def test_available_user_tags(cached_notification_user_tags):
    assert isinstance(cached_notification_user_tags, list)


def test_available_applications(cached_notification_applications):
    assert isinstance(cached_notification_applications, list)


def test_configure(cached_notification, cached_notification_rules, cached_notification_users,
                   cached_notification_user_tags, cached_notification_applications, cached_user):

    users = []
    for user in cached_notification_users:
        if user['userId'] == cached_user['userId']:
            users.append(user)
            break

    rules = []
    for rule in cached_notification_rules:
        if rule['predicate'] in ['AccountsCreated', 'AccountsDeleted']:
            rules.append(rule)

    response = britive.notifications.configure(
        notification_id=cached_notification['notificationId'],
        users=users,
        rules=rules,
        send_no_changes=True
    )

    assert isinstance(response, dict)
    assert response['sendNoChanges']
    assert len(response['recipientUsers']) == 1
    assert len(response['rules']) == 2


def test_delete(cached_notification):
    response = britive.notifications.delete(notification_id=cached_notification['notificationId'])
    assert response is None
    cleanup('notification')
    cleanup('notification-available-rules')
    cleanup('notification-available-users')
    cleanup('notification-available-user-tags')
    cleanup('notification-available-applications')

