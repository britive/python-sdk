from britive.exceptions.generic import BritiveGenericException

from .cache import *  # will also import some globals like `britive`


def test_identity_provider_list():
    response = britive.identity_management.workload.identity_providers.list()
    assert isinstance(response, list)


def test_identity_provider_create_aws(cached_workload_identity_provider_aws):
    # doing less work in the validation here (vs oidc) since an aws provider can already
    # exist and we are only allowed to create 1 per tenant
    assert isinstance(cached_workload_identity_provider_aws, dict)
    assert 'id' in cached_workload_identity_provider_aws


def test_identity_provider_create_oidc(cached_workload_identity_provider_oidc):
    assert isinstance(cached_workload_identity_provider_oidc, dict)
    assert 'id' in cached_workload_identity_provider_oidc
    assert cached_workload_identity_provider_oidc['name'].startswith('pysdktest-oidc')
    assert isinstance(cached_workload_identity_provider_oidc['attributesMap'], list)
    assert len(cached_workload_identity_provider_oidc['attributesMap']) == 1


def test_identity_provider_get(cached_workload_identity_provider_oidc):
    response = britive.identity_management.workload.identity_providers.get(
        workload_identity_provider_id=cached_workload_identity_provider_oidc['id']
    )
    assert isinstance(response, dict)
    assert response['id'] == cached_workload_identity_provider_oidc['id']


def test_identity_provider_update_aws(cached_workload_identity_provider_aws):
    # we may very well need to set the update back to what it was originally as
    # we can only have 1 aws provider, so we want to restore that provider to its
    # original state
    existing_max_duration = britive.identity_management.workload.identity_providers.get(
        workload_identity_provider_id=cached_workload_identity_provider_aws['id']
    )['maxDuration']

    # do the update
    response = britive.identity_management.workload.identity_providers.update_aws(
        workload_identity_provider_id=cached_workload_identity_provider_aws['id'], max_duration=1
    )
    assert isinstance(response, dict)
    assert response['maxDuration'] == 1

    # restore it back
    britive.identity_management.workload.identity_providers.update_aws(
        workload_identity_provider_id=cached_workload_identity_provider_aws['id'], max_duration=existing_max_duration
    )


def test_identity_provider_update_oidc(cached_workload_identity_provider_oidc):
    response = britive.identity_management.workload.identity_providers.update_oidc(
        workload_identity_provider_id=cached_workload_identity_provider_oidc['id'],
        issuer_url='https://id2.fakedomain.com',
    )
    assert isinstance(response, dict)
    assert response['issuerUrl'] == 'https://id2.fakedomain.com'


def test_generate_attribute_map(cached_identity_attribute):
    response = britive.identity_management.workload.identity_providers.generate_attribute_map(
        idp_attribute_name='sub', custom_identity_attribute_id=cached_identity_attribute['id']
    )
    assert isinstance(response, dict)
    assert 'idpAttr' in response
    assert 'userAttr' in response
    assert response['idpAttr'] == 'sub'
    assert response['userAttr'] == cached_identity_attribute['id']

    response = britive.identity_management.workload.identity_providers.generate_attribute_map(
        idp_attribute_name='sub', custom_identity_attribute_name=cached_identity_attribute['name']
    )
    assert isinstance(response, dict)
    assert 'idpAttr' in response
    assert 'userAttr' in response
    assert response['idpAttr'] == 'sub'
    assert response['userAttr'] == cached_identity_attribute['id']


def test_service_identity_get_when_nothing_associated(cached_service_identity_federated):
    with pytest.raises(BritiveGenericException):
        britive.identity_management.workload.service_identities.get(
            service_identity_id=cached_service_identity_federated['userId']
        )


def test_service_identity_assign_and_unassign(
    cached_service_identity_federated, cached_identity_attribute, cached_workload_identity_provider_oidc
):
    response = britive.identity_management.workload.service_identities.assign(
        service_identity_id=cached_service_identity_federated['userId'],
        idp_id=cached_workload_identity_provider_oidc['id'],
        federated_attributes={cached_identity_attribute['id']: 'test'},
    )
    assert isinstance(response, dict)

    attrs = britive.identity_management.service_identities.custom_attributes.get(
        principal_id=cached_service_identity_federated['userId'], as_dict=True
    )

    assert isinstance(attrs, dict)
    assert len(attrs) == 1
    assert attrs[cached_identity_attribute['id']] == 'test'

    response = britive.identity_management.workload.service_identities.unassign(
        service_identity_id=cached_service_identity_federated['userId']
    )

    assert response is None

    attrs = britive.identity_management.service_identities.custom_attributes.get(
        principal_id=cached_service_identity_federated['userId'], as_dict=False
    )

    assert isinstance(attrs, list)
    assert len(attrs) == 1
    assert attrs[0]['attributeName'] is None

    response = britive.identity_management.workload.service_identities.assign(
        service_identity_id=cached_service_identity_federated['userId'],
        idp_id=cached_workload_identity_provider_oidc['id'],
        federated_attributes={cached_identity_attribute['name']: 'test'},
    )
    assert isinstance(response, dict)

    attrs = britive.identity_management.service_identities.custom_attributes.get(
        principal_id=cached_service_identity_federated['userId'], as_dict=True
    )

    assert isinstance(attrs, dict)
    assert len(attrs) == 1
    assert attrs[cached_identity_attribute['id']] == 'test'

    response = britive.identity_management.workload.service_identities.unassign(
        service_identity_id=cached_service_identity_federated['userId']
    )

    assert response is None

    attrs = britive.identity_management.service_identities.custom_attributes.get(
        principal_id=cached_service_identity_federated['userId'], as_dict=False
    )

    assert isinstance(attrs, list)
    assert len(attrs) == 1
    assert attrs[0]['attributeName'] is None


def test_identity_provider_delete(cached_workload_identity_provider_oidc, cached_workload_identity_provider_aws):
    try:
        # we do not want to delete the pre-existing aws provider
        if cached_workload_identity_provider_aws['name'].startswith('pysdktest-aws'):
            aws = britive.identity_management.workload.identity_providers.delete(
                workload_identity_provider_id=cached_workload_identity_provider_aws['id']
            )
            assert aws is None
        oidc = britive.identity_management.workload.identity_providers.delete(
            workload_identity_provider_id=cached_workload_identity_provider_oidc['id']
        )
        assert oidc is None
    finally:
        cleanup('workload-identity-provider-oidc')
        cleanup('workload-identity-provider-aws')
