
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

        params = {}
        if not csv:
            params['page'] = 0
            params['size'] = 100  # 100 is max
        return self.britive.get(f'{self.base_url}/{report_id}{"/csv" if csv else ""}', params=params)
