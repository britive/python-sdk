from .cache import *

def test_get(cached_response_template):
    template = britive.access_broker.response_templates.get(response_template_id=cached_response_template['templateId'])
    assert isinstance(template, dict)

def test_create(cached_response_template):
    assert isinstance(cached_response_template, dict)

def test_list():
    templates = britive.access_broker.response_templates.list()
    assert isinstance(templates, list)
    assert len(templates) > 0

def test_update(cached_response_template):
    template = britive.access_broker.response_templates.update(
        response_template_id=cached_response_template['templateId'],
        description='test2',
        name=cached_response_template['name']
    )
    assert isinstance(template, dict)
    assert template['description'] == 'test2'

