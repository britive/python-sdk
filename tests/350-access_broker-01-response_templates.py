from .cache import *


def test_get(cached_access_broker_response_template):
    template = britive.access_broker.response_templates.get(
        response_template_id=cached_access_broker_response_template['templateId']
    )
    assert isinstance(template, dict)


def test_create(cached_access_broker_response_template):
    assert isinstance(cached_access_broker_response_template, dict)


def test_list():
    templates = britive.access_broker.response_templates.list()
    assert isinstance(templates, list)
    assert len(templates) > 0


def test_update(cached_access_broker_response_template, timestamp):
    template = britive.access_broker.response_templates.update(
        response_template_id=cached_access_broker_response_template['templateId'],
        name=cached_access_broker_response_template['name'],
        description=f'{timestamp}-update',
    )
    assert isinstance(template, dict)
    assert template['description'] == f'{timestamp}-update'
