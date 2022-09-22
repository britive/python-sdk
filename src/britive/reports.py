import csv as csv_lib
from io import StringIO
import json


def _json_loads(value):
    try:
        return json.loads(value)
    except:
        return value


class Reports:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/reports'

    def list(self) -> list:
        """
        Return list of all built-in reports.

        :return: List of reports.
        """

        params = {
            'type': 'report'
        }
        return self.britive.get(self.base_url, params=params)

    def run(self, report_id: str, csv: bool = False) -> any:
        """
        Run a report.

        :param report_id: The ID of the report.
        :param csv: If True the result will be returned as a CSV string. If False (default) the result will be returned
            as a list where each time in the list is a dict representing the row of data.
        :return: CSV string or list.
        """

        csv_results = self.britive.get(f'{self.base_url}/{report_id}/csv')

        # convert csv to json - issue is that JSON response has max of 1k records returned so have to use CSV
        # as the base and convert to dict if the client asked for dict
        if csv:
            return csv_results
        else:
            dict_results = []
            for row in csv_lib.DictReader(StringIO(csv_results), quoting=csv_lib.QUOTE_MINIMAL):
                dict_results.append({k: _json_loads(v) for k, v in row.items()})
            return dict_results


