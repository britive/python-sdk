from .cache import *  # will also import some globals like `britive`


def test_list():
    reports = britive.reports.list()
    assert isinstance(reports, list)
    assert len(reports) >= 10  # at least 10 built-in reports exist so will alway be 10 for sure


def test_run_json():
    for report in britive.reports.list():
        if report['name'] == 'Profile Last Access':
            report_id = report['reportId']

    report = britive.reports.run(report_id=report_id, csv=False)
    assert isinstance(report, list)
    assert len(report) > 5  # at least 5 rows in the report
    assert(len(report)) % 100 != 0  # v2.8.1 - adding check due to pagination bug not including the last page


def test_run_csv():
    for report in britive.reports.list():
        if report['name'] == 'Profile Last Access':
            report_id = report['reportId']

    report = britive.reports.run(report_id=report_id, csv=True)
    assert isinstance(report, str)
    assert 'application,environment,applicationStatus' in report

