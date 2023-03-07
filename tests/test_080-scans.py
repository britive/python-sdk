import time
from .cache import *  # will also import some globals like `britive`


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_scan(cached_scan):
    assert isinstance(cached_scan, dict)
    assert 'taskId' in cached_scan.keys()


# warning - this will take a while if a scan was just initiated! grab and coffee and come back later
@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_status(cached_scan):
    while True:
        status = britive.scans.status(task_id=cached_scan['taskId'])
        if status['status'] == 'Success':
            break
        if status['status'] == 'Error':
            break
        time.sleep(10)
    assert status['status'] == 'Success'


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_history(cached_application):
    response = britive.scans.history(application_id=cached_application['appContainerId'])
    assert isinstance(response, list)
    assert len(response) > 0


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_diff_accounts(cached_application, cached_environment):
    response = britive.scans.diff(
        resource='accounts',
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )
    assert isinstance(response, list)
    assert len(response) > 0


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_diff_groups(cached_application, cached_environment):
    response = britive.scans.diff(
        resource='groups',
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )
    assert isinstance(response, list)
    assert len(response) > 0


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_diff_permissions(cached_application, cached_environment):
    response = britive.scans.diff(
        resource='permissions',
        application_id=cached_application['appContainerId'],
        environment_id=cached_environment['id']
    )
    assert isinstance(response, list)
    assert len(response) > 0
