from datetime import datetime, timedelta, timezone
from typing import Any, Union

import requests

from ..exceptions import AuditLogCsvDownloadError


class Logs:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/logs/v2'

    def fields(self) -> dict:
        """
        Return list of fields that be can used in a filter for an audit query.

        :return: Dict of field keys to field names.
        """

        return self.britive.get(f'{self.base_url}/fields')

    def operators(self) -> dict:
        """
        Return the list of operators that can be used in a filter for an audit query.

        :return: Dict of operator keys to operator names.
        """

        return self.britive.get(f'{self.base_url}/operators')

    def query(
        self,
        from_time: Union[datetime, str, int] = None,
        to_time: Union[datetime, str, int] = None,
        filter_expression: str = None,
        csv: bool = False,
    ) -> Any:
        """
        Retrieve audit log events.

        `csv` options:

            - True: A CSV string is returned. The caller must persist the CSV string to disk.
            - False: A python list of audit events is returned.

        Both `from_time` and `to_time` accept either a `datetime.datetime` object or a value understood directly
        by the audit API. Accepted API values include ISO-8601 timestamps, epoch seconds, epoch milliseconds, and
        relative expressions such as `now`, `yesterday`, or `1 day ago`. When a value without a timezone is provided
        the API treats it as UTC; when a timezone offset is provided the API honors it.

        :param from_time: Lower end of the time frame to search. If not provided will default to
            7 days before `to_time`. A `datetime` object will be interpreted as if in UTC timezone so it is up to the
            caller to ensure that the datetime object represents UTC (no timezone manipulation is performed). A string
            or int is passed through to the audit API as-is (e.g. `'1 day ago'`, `'2026-06-01T00:00:00Z'`, epoch).
        :param to_time: Upper end of the time frame to search. If not provided will default to
            `datetime.datetime.now(timezone.utc)`. A `datetime` object will be interpreted as if in UTC timezone so it
            is up to the caller to ensure that the datetime object represents UTC (no timezone manipulation is
            performed). A string or int is passed through to the audit API as-is.
            Note: the audit API allows a maximum time frame of 7 days between `from_time` and `to_time`.
        :param filter_expression: The expression used to filter the results. A list of available fields and operators
            can be found using `britive.audit_logs.logs.fields` and `britive.audit_logs.logs.operators`, respectively.
            Multiple filter expressions must be joined together by `and`. No other join operator is support.
            Example: actor.displayName co "bob" and event.displayName eq "application"
        :param csv: Will result in a CSV string of the audit events being returned instead of a python list of events.
        :return: Either python list of events (dicts) or CSV string.
        :raises: ValueError - If both `from_time` and `to_time` are `datetime` objects and `from_time` is greater
            than `to_time`. When either bound is a string/int it is left to the audit API to validate.
        """

        if to_time is None:
            to_time = datetime.now(timezone.utc)
        if from_time is None:
            # default the lower bound to 7 days before the upper bound when the upper bound is a datetime;
            # otherwise (a passed-through string/int) fall back to 7 days before now.
            base = to_time if isinstance(to_time, datetime) else datetime.now(timezone.utc)
            from_time = base - timedelta(days=7)

        # only enforce ordering when both bounds are datetimes; string/int values are validated by the audit API
        if isinstance(from_time, datetime) and isinstance(to_time, datetime) and from_time > to_time:
            raise ValueError('from_time must occur before to_time.')

        # a datetime is sent as a UTC ISO-8601 timestamp with a trailing `Z`; a string/int (ISO, epoch, or a
        # relative expression like '1 day ago') is passed through untouched for the audit API to interpret.
        def fmt(value):
            if isinstance(value, datetime):
                return value.isoformat(sep='T', timespec='seconds').split('+')[0] + 'Z'
            return value

        params = {'from': fmt(from_time), 'to': fmt(to_time)}
        if filter_expression:
            params['filter'] = filter_expression

        if csv:
            return self._download_csv(params)

        params['size'] = 200
        return self.britive.get(self.base_url, params=params)

    def _download_csv(self, params: dict) -> str:
        # The v2 CSV export endpoint does not return the CSV content directly. Instead it returns a presigned
        # S3 download URL. To preserve the v1 behavior of returning the CSV as a string, download the file from
        # the presigned URL and return its content. The presigned URL is self-contained and must be requested
        # without the Britive authorization header (S3 rejects unexpected headers), so a bare request is used.
        details = self.britive.get(f'{self.base_url}/csv', params=params)
        try:
            response = requests.get(details['downloadUrl'], timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise AuditLogCsvDownloadError(
                'Retrieved the audit log CSV download URL from the Britive tenant but failed to download the file '
                'from the presigned S3 URL. Ensure the execution environment has outbound HTTPS access to AWS S3 '
                f'(*.s3.amazonaws.com). Underlying error: {e}'
            ) from e
        return response.content.decode('utf-8')
