from .cache import *  # will also import some globals like `britive`


def test_get(cached_task_service):
    assert isinstance(cached_task_service, dict)
    assert cached_task_service['name'] == 'environmentScanner'
    assert cached_task_service['taskType'] == 'ApplicationScanner'


def test_enable(cached_task_service):
    response = britive.task_services.enable(task_service_id=cached_task_service['taskServiceId'])
    assert isinstance(response, dict)
    assert response['enabled']


def test_disable(cached_task_service):
    response = britive.task_services.disable(task_service_id=cached_task_service['taskServiceId'])
    assert isinstance(response, dict)
    assert not response['enabled']