import datetime


class AuditLogs:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/logs'

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

    def query(self, from_time: datetime = None, to_time: datetime = None, filter_expression: str = None,
              csv: bool = False) -> any:
        """
        Retrieve audit log events.

        `csv` options:

            - True: A CSV string is returned. The caller must persist the CSV string to disk.
            - False: A python list of audit events is returned.

        :param from_time: Lower end of the time frame to search. If not provided will default to
            7 days before `to_time`. `from_time` will be interpreted as if in UTC timezone so it is up to the caller to
            ensure that the datetime object represents UTC. No timezone manipulation will occur.
        :param to_time: Upper end of the time frame to search. If not provided will default to
            `datetime.datetime.utcnow()`. `to_time` will be interpreted as if in UTC timezone so it is up to the caller
            to ensure that the datetime object represents UTC. No timezone manipulation will occur.
        :param filter_expression: The expression used to filter the results. A list of available fields and operators
            can be found by querying `britive.audit_logs.fields()` and `britive.audit_logs.operators`, respectively.
            Multiple filter expressions must be joined together by `and`. No other join operator is support.
            Example: actor.displayName co "bob" and event.displayName eq "application"
        :param csv: Will result in a CSV string of the audit events being returned instead of a python list of events.
        :return: Either python list of events (dicts) or CSV string.
        :raises: ValueError - If from_time is greater than to_time.
        """

        to_time = to_time or datetime.datetime.utcnow()
        from_time = from_time or to_time - datetime.timedelta(days=7)

        if from_time > to_time:
            raise ValueError('from_time must occur before to_time.')

        params = {
            'from': from_time.isoformat(sep='T', timespec='seconds') + 'Z',
            'to': to_time.isoformat(sep='T', timespec='seconds') + 'Z'
        }
        if filter_expression:
            params['filter'] = filter_expression
        if not csv:
            params['size'] = 200

        return self.britive.get(f'{self.base_url}{"/csv" if csv else ""}', params=params)
