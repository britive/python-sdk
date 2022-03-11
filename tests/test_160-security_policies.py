from .cache import *  # will also import some globals like `britive`


def test_create(cached_security_policy):
    assert isinstance(cached_security_policy, dict)


def test_list(cached_security_policy):
    policies = britive.security_policies.list()
    assert isinstance(policies, list)
    assert cached_security_policy['id'] in [p['id'] for p in policies]


def test_get(cached_security_policy):
    policy = britive.security_policies.get(security_policy_id=cached_security_policy['id'])
    assert isinstance(policy, dict)


def test_disable(cached_security_policy):
    response = britive.security_policies.disable(security_policy_id=cached_security_policy['id'])
    assert response is None
    policy = britive.security_policies.get(security_policy_id=cached_security_policy['id'])
    assert policy['status'] == 'Inactive'


def test_enable(cached_security_policy):
    response = britive.security_policies.enable(security_policy_id=cached_security_policy['id'])
    assert response is None
    policy = britive.security_policies.get(security_policy_id=cached_security_policy['id'])
    assert policy['status'] == 'Active'


def test_update(cached_security_policy):
    response = britive.security_policies.update(
        security_policy_id=cached_security_policy['id'],
        ips=['2.2.2.2']
    )
    assert response is None

    policy = britive.security_policies.get(security_policy_id=cached_security_policy['id'])
    assert policy['conditions'][0]['values'] == ['2.2.2.2']


def test_delete(cached_security_policy):
    response = britive.security_policies.delete(security_policy_id=cached_security_policy['id'])
    assert response is None
    cleanup('security-policy')
