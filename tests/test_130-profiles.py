import os
import json
from .cache import *  # will also import some globals like `britive`


def test_create(cached_profile):
    assert isinstance(cached_profile, dict)
    assert cached_profile['name'].startswith('test')
    assert len(cached_profile['scope']) == 0


def test_list(cached_profile):
    profiles = britive.profiles.list(application_id=cached_profile['appContainerId'])
    assert isinstance(profiles, list)
    assert len(profiles) > 0
    assert isinstance(profiles[0], dict)
    assert profiles[0]['name'].startswith('test')


def test_get(cached_profile):
    profile = britive.profiles.get(application_id=cached_profile['appContainerId'], profile_id=cached_profile['papId'])
    assert isinstance(profile, dict)
    assert profile['name'].startswith('test')


def test_update(cached_profile):
    profile = britive.profiles.update(
        application_id=cached_profile['appContainerId'],
        profile_id=cached_profile['papId'],
        description='test desc'
    )
    assert isinstance(profile, dict)
    assert profile['description'] == 'test desc'


def test_set_scopes(cached_profile, cached_environment):
    scopes = britive.profiles.set_scopes(
        profile_id=cached_profile['papId'],
        scopes=[
            {
                'type': 'Environment',
                'value': cached_environment['id']
            }
        ]
    )
    assert isinstance(scopes, list)
    assert len(scopes) == 1
    assert isinstance(scopes[0], dict)
    assert scopes[0]['value'] == cached_environment['id']


def test_get_scopes(cached_profile, cached_environment):
    scopes = britive.profiles.get_scopes(profile_id=cached_profile['papId'])
    assert isinstance(scopes, list)
    assert len(scopes) == 1
    assert isinstance(scopes[0], dict)
    assert scopes[0]['value'] == cached_environment['id']


def test_remove_single_environment_scope(cached_profile, cached_environment):
    response = britive.profiles.remove_single_environment_scope(
        profile_id=cached_profile['papId'],
        environment_id=cached_environment['id']
    )
    assert response is None


def test_add_single_environment_scope(cached_profile, cached_environment):
    response = britive.profiles.add_single_environment_scope(
        profile_id=cached_profile['papId'],
        environment_id=cached_environment['id']
    )
    assert response is None


def test_disable(cached_profile):
    profile = britive.profiles.disable(
        application_id=cached_profile['appContainerId'],
        profile_id=cached_profile['papId']
    )
    assert isinstance(profile, dict)
    assert profile['status'] == 'inactive'


def test_enable(cached_profile):
    profile = britive.profiles.enable(
        application_id=cached_profile['appContainerId'],
        profile_id=cached_profile['papId']
    )
    assert isinstance(profile, dict)
    assert profile['status'] == 'active'


def test_session_attributes_add_static(cached_static_session_attribute):
    assert isinstance(cached_static_session_attribute, dict)


def test_session_attributes_add_dynamic(cached_dynamic_session_attribute):
    assert isinstance(cached_dynamic_session_attribute, dict)


def test_session_attributes_list(cached_profile):
    attributes = britive.profiles.session_attributes.list(profile_id=cached_profile['papId'])
    assert isinstance(attributes, list)
    assert len(attributes) == 2


def test_session_attributes_update_static(cached_profile, cached_static_session_attribute):
    attribute = britive.profiles.session_attributes.update_static(
        profile_id=cached_profile['papId'],
        attribute_id=cached_static_session_attribute['id'],
        tag_name='test-static-2',
        tag_value='test',
        transitive=True
    )
    assert attribute is None


def test_session_attributes_update_dynamic(cached_profile, cached_dynamic_session_attribute):
    attribute = britive.profiles.session_attributes.update_dynamic(
        profile_id=cached_profile['papId'],
        attribute_id=cached_dynamic_session_attribute['id'],
        identity_attribute_id='w2zQ4R9xoyrkWY4phEV9',
        tag_name='test-dynamic-2',
        transitive=True
    )
    assert attribute is None


def test_session_attributes_remove(cached_profile, cached_static_session_attribute, cached_dynamic_session_attribute):
    try:
        static = britive.profiles.session_attributes.remove(
            profile_id=cached_profile['papId'],
            attribute_id=cached_static_session_attribute['id']
        )
        assert static is None

        dynamic = britive.profiles.session_attributes.remove(
            profile_id=cached_profile['papId'],
            attribute_id=cached_dynamic_session_attribute['id']
        )
        assert dynamic is None
    finally:
        for resource in ['static', 'dynamic']:
            file = f'./.cache/v/resources/{resource}-session-attribute'
            if os.path.isfile(file):
                os.remove(file)


def test_policies_create(cached_profile_policy):
    print(cached_profile_policy)
    assert isinstance(cached_profile_policy, dict)
    assert cached_profile_policy['members']['tags']


def test_list_include_policies(cached_profile):
    profiles = britive.profiles.list(application_id=cached_profile['appContainerId'], include_policies=True)
    assert isinstance(profiles, list)
    assert len(profiles) > 0
    assert isinstance(profiles[0], dict)
    assert profiles[0]['profileName'].startswith('test')
    assert 'policies' in profiles[0]


def test_disable_mfa(cached_profile, cached_tag, cached_profile_policy):
    profile_policy = britive.profiles.policies.build(
        name=cached_profile['papId'],
        description=cached_tag['name'],
        active=False,
        stepup_auth=False,
        always_prompt_stepup_auth=False
    )
    response = britive.profiles.policies.update(
        profile_id=cached_profile['papId']
        , policy_id=cached_profile_policy['id']
        , policy=profile_policy
    )
    response = britive.profiles.policies.get(
        profile_id=cached_profile['papId']
        , policy_id=cached_profile_policy['id']
    )
    assert isinstance(json.loads(response.get('condition')), dict)
    assert json.loads(response.get('condition')).get('stepUpCondition', '') == ''


def test_enable_mfa(cached_profile, cached_tag, cached_profile_policy):
    profile_policy = britive.profiles.policies.build(
        name=cached_profile['papId'],
        description=cached_tag['name'],
        active=False,
        stepup_auth=True,
        always_prompt_stepup_auth=False
    )
    response = britive.profiles.policies.update(
        profile_id=cached_profile['papId']
        , policy_id=cached_profile_policy['id']
        , policy=profile_policy
    )
    response = britive.profiles.policies.get(
        profile_id=cached_profile['papId']
        , policy_id=cached_profile_policy['id']
    )
    assert isinstance(json.loads(response.get('condition')), dict)
    assert json.loads(response.get('condition')).get('stepUpCondition').get('factor') == 'TOTP'


def test_policies_create_with_approval_single_notification_medium(cached_profile_approval_policy):
    assert isinstance(cached_profile_approval_policy, dict)
    assert cached_profile_approval_policy['members']['serviceIdentities']


def test_policies_create_with_approval_multiple_notification_medium(cached_profile, cached_service_identity):
    policy = britive.profiles.policies.build(
        name=f"{cached_profile['papId']}-2",
        description='',
        service_identities=[cached_service_identity['username']],
        approval_notification_medium=['Email'],
        approver_users=[britive.my_access.whoami()['username']]
    )
    assert isinstance(policy, dict)


def test_policies_list(cached_profile):
    policies = britive.profiles.policies.list(profile_id=cached_profile['papId'])
    assert isinstance(policies, list)


def test_policies_get(cached_profile, cached_profile_policy):
    policy = britive.profiles.policies.get(
        profile_id=cached_profile['papId'],
        policy_id=cached_profile_policy['id']
    )
    assert isinstance(policy, dict)


def test_policies_condition_created_as_json_get_formatted_json(cached_profile, cached_profile_policy_condition_as_json_str):
    policy = britive.profiles.policies.get(
        profile_id=cached_profile['papId'],
        policy_id=cached_profile_policy_condition_as_json_str['id'], condition_as_dict=False
    )
    assert isinstance(policy['condition'], str)


def test_policies_condition_created_as_json_get_formatted_dict(cached_profile, cached_profile_policy_condition_as_json_str):
    policy = britive.profiles.policies.get(
        profile_id=cached_profile['papId'],
        policy_id=cached_profile_policy_condition_as_json_str['id'],
        condition_as_dict=True
    )
    assert isinstance(policy['condition'], dict)


def test_policies_condition_created_as_dict_get_formatted_json(cached_profile, cached_profile_policy_condition_as_dict):
    policy = britive.profiles.policies.get(
        profile_id=cached_profile['papId'],
        policy_id=cached_profile_policy_condition_as_dict['id'], condition_as_dict=False
    )
    assert isinstance(policy['condition'], str)


def test_policies_condition_created_as_dict_get_formatted_dict(cached_profile, cached_profile_policy_condition_as_dict):
    policy = britive.profiles.policies.get(
        profile_id=cached_profile['papId'],
        policy_id=cached_profile_policy_condition_as_dict['id'], condition_as_dict=True
    )
    assert isinstance(policy['condition'], dict)


def test_policies_update(cached_profile, cached_profile_policy):
    policy = {
        'members': {
            'tags': [
                {'id': tag['id']}
                for tag in cached_profile_policy['members']['tags']
            ]
        }
    }
    assert britive.profiles.policies.update(
        profile_id=cached_profile['papId'],
        policy_id=cached_profile_policy['id'],
        policy=policy
    ) is None


def test_policies_delete(cached_profile, cached_profile_policy):
    try:
        assert britive.profiles.policies.delete(
            profile_id=cached_profile['papId'],
            policy_id=cached_profile_policy['id']
        ) is None
    finally:
        cleanup('profile-policy')


@pytest.mark.skipif(constraints, reason=constraints_skip)
def test_constraints_list_supported_types(cached_gcp_profile_big_query, cached_gcp_profile_storage):
    response = britive.profiles.permissions.constraints.list_supported_types(
        profile_id=cached_gcp_profile_big_query['papId'],
        permission_name='BigQuery Admin',
        permission_type='role'
    )
    assert 'bigquery.datasets' in response
    assert 'bigquery.tables' in response

    response = britive.profiles.permissions.constraints.list_supported_types(
        profile_id=cached_gcp_profile_storage['papId'],
        permission_name='Storage Admin',
        permission_type='role'
    )

    assert len(response) == 1
    assert 'condition' in response


@pytest.mark.skipif(constraints, reason=constraints_skip)
def test_constraints_get_before_add(cached_gcp_profile_big_query, cached_gcp_profile_storage):
    response = britive.profiles.permissions.constraints.get(
        profile_id=cached_gcp_profile_big_query['papId'],
        permission_name='BigQuery Admin',
        permission_type='role',
        constraint_type='bigquery.datasets'
    )

    assert response is None

    response = britive.profiles.permissions.constraints.get(
        profile_id=cached_gcp_profile_big_query['papId'],
        permission_name='BigQuery Admin',
        permission_type='role',
        constraint_type='bigquery.tables'
    )

    assert response is None

    response = britive.profiles.permissions.constraints.get(
        profile_id=cached_gcp_profile_storage['papId'],
        permission_name='Storage Admin',
        permission_type='role',
        constraint_type='condition'
    )

    assert response is None


@pytest.mark.skipif(constraints, reason=constraints_skip)
def test_constraints_lint_condition(cached_gcp_profile_storage):
    expression = "(resource.type != 'storage.googleapis.com/Bucket' && " \
                 "resource.type != 'storage.googleapis.com/Object') || " \
                 "resource.name.startsWith('projects/_/buckets/my-first-project-demo-bucket-1')"
    response = britive.profiles.permissions.constraints.lint_condition(
        profile_id=cached_gcp_profile_storage['papId'],
        permission_name='Storage Admin',
        permission_type='role',
        expression=expression
    )

    assert response['success']
    assert response['message'] == '{}'


@pytest.mark.skipif(constraints, reason=constraints_skip)
def test_constraints_add_big_query(cached_gcp_profile_big_query):
    response = britive.profiles.permissions.constraints.add(
        profile_id=cached_gcp_profile_big_query['papId'],
        permission_name='BigQuery Admin',
        permission_type='role',
        constraint_type='bigquery.datasets',
        constraint='my-first-project-310615.myfirstdataset'
    )

    assert response is None

    try:
        britive.profiles.permissions.constraints.add(
            profile_id=cached_gcp_profile_big_query['papId'],
            permission_name='BigQuery Admin',
            permission_type='role',
            constraint_type='bigquery.datasets',
            constraint='my-first-project-310615.myfirstdataset'
        )
    except Exception as e:
        assert 'Constraint is already available in the added list' in str(e)


@pytest.mark.skipif(constraints, reason=constraints_skip)
def test_constraints_add_storage(cached_gcp_profile_storage):
    expression = "(resource.type != 'storage.googleapis.com/Bucket' && " \
                 "resource.type != 'storage.googleapis.com/Object') || " \
                 "resource.name.startsWith('projects/_/buckets/my-first-project-demo-bucket-1')"

    constraint = {
        'title': 'test',
        'description': 'test',
        'expression': expression
    }

    response = britive.profiles.permissions.constraints.add(
        profile_id=cached_gcp_profile_storage['papId'],
        permission_name='Storage Admin',
        permission_type='role',
        constraint_type='condition',
        constraint=constraint
    )

    assert response is None

    try:
        britive.profiles.permissions.constraints.add(
            profile_id=cached_gcp_profile_storage['papId'],
            permission_name='Storage Admin',
            permission_type='role',
            constraint_type='condition',
            constraint=constraint
        )
    except Exception as e:
        assert 'Constraint is already available in the added list' in str(e)


@pytest.mark.skipif(constraints, reason=constraints_skip)
def test_constraints_remove_big_query(cached_gcp_profile_big_query):
    try:
        response = britive.profiles.permissions.constraints.remove(
            profile_id=cached_gcp_profile_big_query['papId'],
            permission_name='BigQuery Admin',
            permission_type='role',
            constraint_type='bigquery.datasets',
            constraint='my-first-project-310615.myfirstdataset'
        )

        assert response is None
    finally:
        britive.profiles.delete(
            application_id=os.getenv('BRITIVE_GCP_TEST_APP_ID'),
            profile_id=cached_gcp_profile_big_query['papId']
        )
        cleanup('gcp-profile-bq')


@pytest.mark.skipif(constraints, reason=constraints_skip)
def test_constraints_remove_storage(cached_gcp_profile_storage):
    try:
        response = britive.profiles.permissions.constraints.remove(
            profile_id=cached_gcp_profile_storage['papId'],
            permission_name='Storage Admin',
            permission_type='role',
            constraint_type='condition',
            constraint=None
        )

        assert response is None
    finally:
        britive.profiles.delete(
            application_id=os.getenv('BRITIVE_GCP_TEST_APP_ID'),
            profile_id=cached_gcp_profile_storage['papId']
        )
        cleanup('gcp-profile-storage')
