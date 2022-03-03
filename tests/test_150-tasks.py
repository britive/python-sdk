from .cache import *  # will also import some globals like `britive`


def test_create(cached_task):
    assert isinstance(cached_task, dict)
    assert cached_task['name'] == 'test'


def test_list(cached_task_service):
    tasks = britive.tasks.list(task_service_id=cached_task_service['taskServiceId'])
    assert isinstance(tasks, list)
    assert len(tasks) == 1
    assert tasks[0]['name'] == 'test'


def test_get(cached_task_service, cached_task):
    task = britive.tasks.get(task_service_id=cached_task_service['taskServiceId'], task_id=cached_task['taskId'])
    assert isinstance(task, dict)
    assert task['name'] == 'test'


def test_update(cached_task_service, cached_task):
    task = britive.tasks.update(
        task_service_id=cached_task_service['taskServiceId'],
        task_id=cached_task['taskId'],
        name='test2'
    )
    assert isinstance(task, dict)
    assert task['name'] == 'test2'


def test_delete(cached_task_service, cached_task):
    task = britive.tasks.delete(task_service_id=cached_task_service['taskServiceId'], task_id=cached_task['taskId'])
    assert task is None
    tasks = britive.tasks.list(task_service_id=cached_task_service['taskServiceId'])
    assert len(tasks) == 0
    cleanup('task')

