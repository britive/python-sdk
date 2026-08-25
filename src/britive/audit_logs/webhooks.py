import contextlib

import jmespath
from jmespath.exceptions import EmptyExpressionError, ParseError


class Webhooks:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/notification-service/logs/webhooks'

    def create_or_update(self, notification_medium_id: str, jmespath_filter: str = '', description: str = '') -> dict:
        """
        Create an audit log webhook, or update the webhook for an existing notification medium.

        :param notification_medium_id: Notification medium ID for the webhook.
        :param jmespath_filter: JMESPath filter to apply before sending audit events to the webhook.
        :param description: Description of the audit log webhook.
        :return: The created or updated audit log webhook.
        """

        try:
            with contextlib.suppress(EmptyExpressionError):
                jmespath.compile(jmespath_filter)
        except ParseError as e:
            raise ValueError('Invalid JMESPath.') from e

        params = {
            'notificationMediumId': notification_medium_id,
            'filter': jmespath_filter,
            'description': description,
        }

        return self.britive.post(f'{self.base_url}', json=params)

    def get(self, notification_medium_id: str) -> dict:
        """
        Return the audit log webhook for a notification medium.

        :param notification_medium_id: Notification medium ID for the webhook.
        :return: The audit log webhook.
        """

        return self.britive.get(f'{self.base_url}/{notification_medium_id}')

    def list(self) -> list:
        """
        Return the tenant's audit log webhooks.

        :return: A list of audit log webhooks.
        """

        return self.britive.get(f'{self.base_url}')

    def delete(self, notification_medium_id: str) -> None:
        """
        Delete the audit log webhook for a notification medium.

        :param notification_medium_id: Notification medium ID for the webhook.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{notification_medium_id}')
