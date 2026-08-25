import os
from datetime import datetime, timedelta, timezone
from sys import stderr
from urllib import parse

import requests

from ..exceptions import BritiveException


class Logs:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/logs/v2'

    def fields(self) -> dict:
        """
        Return the fields that can be used to filter an audit log query.

        :return: Dict of field keys to field names.
        """

        return self.britive.get(f'{self.base_url}/fields')

    def operators(self) -> dict:
        """
        Return the operators that can be used to filter an audit log query.

        :return: Dict of operator keys to operator names.
        """

        return self.britive.get(f'{self.base_url}/operators')

    def query(
        self,
        from_time: datetime | str | int = None,
        to_time: datetime | str | int = None,
        filter_expression: str = None,
        csv: bool = False,
    ) -> list[dict] | str:
        """
        Retrieve audit log events.

        `csv` options:

            - True: Return a CSV string in the legacy format. If direct CSV export fails, generate the CSV locally.
            - False: Return a Python list of audit events.

        Both `from_time` and `to_time` accept either a `datetime.datetime` object or a value understood directly
        by the audit API. Accepted API values include ISO-8601 timestamps, epoch seconds, epoch milliseconds, and
        relative expressions such as `now`, `yesterday`, or `1 day ago`. When a value without a timezone is provided
        the API treats it as UTC; when a timezone offset is provided the API honors it. The SDK passes these values
        without timezone conversion. The audit API limits queries to a maximum range of seven days.

        :param from_time: Lower bound of the query. When omitted with a `datetime` `to_time`, defaults to seven days
            before `to_time`. When omitted with a string or integer `to_time`, defaults to seven days before the current
            UTC time and writes a warning to stderr.
        :param to_time: Upper bound of the query. When omitted, defaults to the current UTC time.
        :param filter_expression: The expression used to filter the results. A list of available fields and operators
            can be found using `britive.audit_logs.logs.fields()` and `britive.audit_logs.logs.operators()`,
            respectively. Multiple filter expressions must be joined by `and`. No other join operator is supported.
            Example: actor.displayName co "bob" and event.displayName eq "application"
        :param csv: Return a legacy-compatible CSV string instead of a list of events.
        :return: A list of audit event dictionaries or a CSV string.
        :raises BritiveException: If the audit API rejects the query. API-specific subclasses are preserved.
        """

        if to_time is None:
            to_time = datetime.now(timezone.utc)
        if from_time is None:
            if isinstance(to_time, datetime):
                from_time = to_time - timedelta(days=7)
            else:
                from_time = datetime.now(timezone.utc) - timedelta(days=7)
                print(
                    f'Warning: Parameter `from_time` was left unspecified. Defaulting to `{from_time.isoformat()}`.',
                    file=stderr,
                )
        params = {'from': from_time, 'to': to_time}

        if filter_expression:
            params['filter'] = filter_expression

        if csv:
            try:
                # THE BELOW REFORMATTING WILL BE REMOVED IN THE NEXT MAJOR RELEASE
                # TODO: replace with self.download_csv(...) in next major release
                csv_data = self.download_csv(
                    from_time=from_time, to_time=to_time, filter_expression=filter_expression
                ).replace(',""\r\n', ',\r\n')
                while ',"",' in csv_data:
                    csv_data = csv_data.replace(',"",', ',,')
                return csv_data.replace(',""\r\n', ',\r\n')
            except BritiveException as error:
                if type(error) is not BritiveException:
                    raise
                print('Warning: v2 CSV retrieval failed - falling back to local CSV generation.', file=stderr)
                return self._local_csv(logs=self.britive.get(self.base_url, params=params))

        return self.britive.get(self.base_url, params=params)

    def download_csv(
        self,
        from_time: datetime | str | int = None,
        to_time: datetime | str | int = None,
        filter_expression: str = None,
        output_file: str | os.PathLike = None,
    ) -> str:
        """
        Download audit log events as CSV content or write them to a file.

        Both `from_time` and `to_time` accept a `datetime.datetime`, an ISO-8601 timestamp, epoch seconds, epoch
        milliseconds, or a relative expression understood by the audit API. The SDK passes these values without
        timezone conversion. The audit API limits queries to a maximum range of seven days.

        The audit API returns a presigned download URL. The SDK requests that URL without the Britive authorization
        header. When `output_file` is provided, the method overwrites that file but does not create parent directories.

        :param from_time: Lower bound of the export. When omitted with a `datetime` `to_time`, defaults to seven days
            before `to_time`. When omitted with a string or integer `to_time`, defaults to seven days before the current
            UTC time and writes a warning to stderr.
        :param to_time: Upper bound of the export. When omitted, defaults to the current UTC time.
        :param filter_expression: The expression used to filter the exported audit events.
        :param output_file: File path for the downloaded CSV. When omitted, return the CSV content as a string.
        :return: The CSV content, or `CSV Downloaded: <output_file>` when `output_file` is provided.
        :raises BritiveException: If the export response has no download URL or the download request fails.
            API-specific subclasses are preserved.
        """

        if to_time is None:
            to_time = datetime.now(timezone.utc)
        if from_time is None:
            if isinstance(to_time, datetime):
                from_time = to_time - timedelta(days=7)
            else:
                from_time = datetime.now(timezone.utc) - timedelta(days=7)
                print(
                    f'Warning: Parameter `from_time` was left unspecified. Defaulting to `{from_time.isoformat()}`.',
                    file=stderr,
                )
        params = {'from': from_time, 'to': to_time}

        if filter_expression:
            params['filter'] = filter_expression

        details = self.britive.get(f'{self.base_url}/csv', params=params)
        try:
            download_url = details['downloadUrl']
        except (KeyError, TypeError):
            raise BritiveException('The audit log CSV export response did not include a download URL.')

        try:
            response = requests.get(download_url, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            s3_domain = parse.urlparse(download_url).netloc
            raise BritiveException(
                'Retrieved the audit log CSV download URL from the Britive tenant but failed to download the file from '
                f'the presigned S3 URL. Ensure the execution environment has outbound HTTPS access to [{s3_domain}].'
            )
        if output_file:
            with open(output_file, mode='wb') as csv_file:
                csv_file.write(response.content)
            return f'CSV Downloaded: {output_file}'
        return response.content.decode('utf-8')

    # THE BELOW LEGACY COVERAGE WILL BE REMOVED IN THE NEXT MAJOR RELEASE: v5.0.0
    # TODO: remove in next major release
    def _local_csv(self, logs: list) -> str:
        def _flatten(data, prefix=''):
            return {
                flat_key: flat_value
                for key, value in data.items()
                for flat_key, flat_value in (
                    _flatten(value, f'{prefix}{key}.').items()
                    if isinstance(value, dict)
                    else ((f'{prefix}{key}', value),)
                )
            }

        def _quote(column, value):
            match column, value:
                case 'timestamp', value if value:
                    value = datetime.fromisoformat(value).strftime('%a %b %d %H:%M:%S UTC %Y')
                case _, bool():
                    value = str(value).lower()
                case column, None if column.endswith('additionalInfo'):
                    value = ' '
                case _, None:
                    return ''

            return '"' + str(value).replace('"', '""') + '"'

        column_map = {
            'timestamp': 'timestamp',
            'actor.display_name': 'actor.displayName',
            'actor.type': 'actor.type',
            'actor.role': 'actor.role',
            'actor.username': 'actor.username',
            'client.device': 'client.device',
            'client.ipAddress': 'client.ipAddress',
            'client.browser': 'client.browser',
            'client.platform': 'client.platform',
            'client.userAgent': 'client.userAgent',
            'client.displayName': 'client.displayName',
            'client.additionalInfo': 'client.additionalInfo',
            'event.eventType': 'event.eventType',
            'event.displayName': 'event.displayName',
            'event.additionalInfo': 'event.additionalInfo',
            'target.applicationName': 'target.applicationName',
            'target.environmentName': 'target.environmentName',
            'target.environmentGroupName': 'target.environmentGroupName',
            'target.parentEnvironmentGroupName': 'target.parentEnvironmentGroupName',
            'target.displayName': 'target.displayName',
            'target.applicationSessionId': 'target.applicationSessionId',
            'target.additionalInfo': 'target.additionalInfo',
            'result.success': 'result.success',
            'result.message': 'result.message',
        }

        rows = [_flatten(row) for row in logs]

        return (
            '\r\n'.join(
                [
                    ','.join(f'"{column}"' for column in column_map),
                    *[
                        ','.join(_quote(column, row.get(source)) for column, source in column_map.items())
                        for row in rows
                    ],
                ]
            )
            + '\r\n'
        )
