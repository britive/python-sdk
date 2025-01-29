import contextlib

import jmespath
from jmespath.exceptions import EmptyExpressionError, ParseError


class Webhooks:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/logs/webhooks'

    def create_or_update(self, notification_medium_id: str, jmespath_filter: str = '', description: str = '') -> dict:
        """
        Return details of a created, or updated if the notificationMediumId already exists, audit log webhook.

        :param notification_medium_id: the notificationMediumId webhook to create or update.
        :param jmespath_filter: a JMESPath filter to apply to log entries before sending to the webhook.
        :param description: the description of the audit log webhook.
        :return: Dict of field keys to field names.
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
        Return audit log webhook details specified by notificationMediumId.

        :param notification_medium_id: the notificationMediumId webhook to retrieve.
        :return: Dict of field keys to field names.
        """

        return self.britive.get(f'{self.base_url}/{notification_medium_id}')

    def list(self) -> list:
        """
        Return a list of audit log webhook details for the tenant.

        :return: List of field keys to field names.
        """

        return self.britive.get(f'{self.base_url}')

    def delete(self, notification_medium_id: str) -> None:
        """
        Delete an audit log webhook specified by notificationMediumId.

        :param notification_medium_id: the notificationMediumId webhook to delete.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{notification_medium_id}')
