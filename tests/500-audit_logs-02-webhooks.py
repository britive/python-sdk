from .cache import *


def test_audit_logs_webhook_create(cached_audit_logs_webhook_create, cached_notification_medium_webhook):
    assert isinstance(cached_audit_logs_webhook_create, dict)
    assert cached_audit_logs_webhook_create['notificationMediumId'] == cached_notification_medium_webhook['id']
    assert "contains('event.eventType', 'checkout')" in cached_audit_logs_webhook_create['filter']
    assert 'python-sdk-aws-audit-log-webhook' in cached_audit_logs_webhook_create['description']
