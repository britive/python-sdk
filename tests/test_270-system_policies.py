from .cache import *  # will also import some globals like `britive`


def test_list():
    response = britive.system.policies.list()
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert 'id' in response[0].keys()
    assert 'name' in response[0].keys()


def test_create(cached_system_level_policy):
    assert isinstance(cached_system_level_policy, dict)
    assert 'id' in cached_system_level_policy.keys()
    assert 'name' in cached_system_level_policy.keys()
    assert cached_system_level_policy['name'].startswith('python-sdk')


def test_create_single_nm(cached_tag):
    policy = britive.system.policies.build(
        name='python-sdk',
        tags=[cached_tag['name']],
        roles=['UserViewRole'],
        approval_notification_medium='Email',
        approver_tags=[cached_tag['name']]
    )

    assert isinstance(policy, dict)
    assert 'name' in policy.keys()
    assert policy['name'].startswith('python-sdk')


def test_create_multiple_nm(cached_tag):
    policy = britive.system.policies.build(
        name='python-sdk',
        tags=[cached_tag['name']],
        roles=['UserViewRole'],
        approval_notification_medium=['Email'],
        approver_tags=[cached_tag['name']]
    )

    assert isinstance(policy, dict)
    assert 'name' in policy.keys()
    assert policy['name'].startswith('python-sdk')


def test_get_id(cached_system_level_policy):
    response = britive.system.policies.get(policy_identifier=cached_system_level_policy['id'], identifier_type='id')
    assert 'id' in response.keys()
    assert 'name' in response.keys()
    assert response['name'].startswith('python-sdk')


def test_get_name(cached_system_level_policy):
    response = britive.system.policies.get(policy_identifier=cached_system_level_policy['name'])
    assert 'id' in response.keys()
    assert 'name' in response.keys()
    assert response['name'].startswith('python-sdk')


def test_update_id(cached_system_level_policy, cached_tag):
    roles = britive.system.roles.list()
    role_ids = []
    roles_to_add = ['ApplicationViewRole', 'TenantAdminRole']
    for role in roles:
        if role['name'] in roles_to_add:
            role_ids.append(role['id'])

    policy = britive.system.policies.build(
        name=cached_system_level_policy['name'],
        tags=[cached_tag['userTagId']],
        roles=role_ids,
        identifier_type='id'
    )
    response = britive.system.policies.update(
        policy_identifier=cached_system_level_policy['id'],
        policy=policy,
        identifier_type='id'
    )

    assert response is None

    response = britive.system.policies.get(policy_identifier=cached_system_level_policy['id'], identifier_type='id')
    assert 'id' in response.keys()
    assert 'name' in response.keys()
    assert response['name'].startswith('python-sdk')
    assert len(response['roles']) == 2


def test_update_name(cached_system_level_policy, cached_tag):
    policy = britive.system.policies.build(
        name=cached_system_level_policy['name'],
        tags=[cached_tag['name']],
        roles=['UserViewRole', 'NMAdminRole', 'ApplicationViewRole']
    )
    response = britive.system.policies.update(
        policy_identifier=cached_system_level_policy['name'],
        policy=policy,
        identifier_type='name'
    )

    assert response is None

    response = britive.system.policies.get(
        policy_identifier=cached_system_level_policy['name'],
        identifier_type='name'
    )
    assert 'id' in response.keys()
    assert 'name' in response.keys()
    assert response['name'].startswith('python-sdk')
    assert len(response['roles']) == 3


def test_disable_id(cached_system_level_policy):
    assert britive.system.policies.disable(
        policy_identifier=cached_system_level_policy['id'],
        identifier_type='id'
    ) is None
    assert britive.system.policies.get(
        policy_identifier=cached_system_level_policy['id'],
        identifier_type='id'
    )['isActive'] is False


def test_enable_id(cached_system_level_policy):
    assert britive.system.policies.enable(
        policy_identifier=cached_system_level_policy['id'],
        identifier_type='id'
    ) is None
    assert britive.system.policies.get(
        policy_identifier=cached_system_level_policy['id'],
        identifier_type='id'
    )['isActive'] is True


def test_disable_name(cached_system_level_policy):
    assert britive.system.policies.disable(policy_identifier=cached_system_level_policy['name']) is None
    assert britive.system.policies.get(
        policy_identifier=cached_system_level_policy['name']
    )['isActive'] is False


def test_enable_name(cached_system_level_policy):
    assert britive.system.policies.enable(policy_identifier=cached_system_level_policy['name']) is None
    assert britive.system.policies.get(
        policy_identifier=cached_system_level_policy['name']
    )['isActive'] is True


def test_delete(cached_system_level_policy):
    try:
        assert britive.system.policies.delete(
            policy_identifier=cached_system_level_policy['id'],
            identifier_type='id'
        ) is None
        assert britive.system.policies.get(cached_system_level_policy['id'])['errorCode'] == 'PA-0045'
    finally:
        cleanup('policy-system-level')


def test_evaluate():
    response = britive.system.policies.evaluate(
        statements=[
            {
                'action': 'authz.permission.update',
                'resource': '*',
                'consumer': 'authz'
            }
        ]
    )
    assert isinstance(response, dict)
    assert len(response.keys()) == 1
    assert 'PolicyEvalRequest' in list(response.keys())[0]
