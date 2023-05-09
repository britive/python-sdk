from .cache import *  # will also import some globals like `britive`
from britive import exceptions


def test_create(cached_identity_provider):
    assert isinstance(cached_identity_provider, dict)


def test_list(cached_identity_provider):
    idps = britive.identity_providers.list()
    assert isinstance(idps, list)
    assert len(idps) > 0
    assert isinstance(idps[0], dict)
    assert cached_identity_provider['id'] in [idp['id'] for idp in idps]


def test_get_by_id(cached_identity_provider):
    idp = britive.identity_providers.get(identity_provider_id=cached_identity_provider['id'])
    assert isinstance(idp, dict)
    assert idp['id'] == cached_identity_provider['id']


def test_get_by_name(cached_identity_provider):
    idp = britive.identity_providers.get_by_name(identity_provider_name=cached_identity_provider['name'])
    assert isinstance(idp, dict)
    assert idp['name'] == cached_identity_provider['name']


def test_update(cached_identity_provider):
    response = britive.identity_providers.update(
        identity_provider_id=cached_identity_provider['id'],
        sso_provider='Azure'
    )
    assert response is None
    idp = britive.identity_providers.get_by_name(identity_provider_name=cached_identity_provider['name'])
    assert isinstance(idp, dict)
    assert idp['ssoProvider'] == 'Azure'


def test_scim_token_create(cached_scim_token):
    assert isinstance(cached_scim_token, dict)
    assert cached_scim_token['tokenExpirationDays'] == 60


def test_scim_token_get(cached_scim_token, cached_identity_provider):
    token = britive.identity_providers.scim_tokens.get(identity_provider_id=cached_identity_provider['id'])
    assert isinstance(token, dict)
    assert token['name'] == cached_scim_token['name']


def test_scim_token_update(cached_identity_provider):
    response = britive.identity_providers.scim_tokens.update(
        identity_provider_id=cached_identity_provider['id'],
        token_expiration_days=30
    )
    assert response is None
    token = britive.identity_providers.scim_tokens.get(identity_provider_id=cached_identity_provider['id'])
    assert token['tokenExpirationDays'] == 30


def test_scim_attributes_list():
    attributes = britive.identity_providers.scim_attributes.list()
    assert isinstance(attributes, list)
    assert len(attributes) > 0
    assert isinstance(attributes[0], str)


def test_scim_tokens_update_attribute_mapping(cached_identity_provider):

    attributes = britive.identity_attributes.list()
    phone_id = None
    for attribute in attributes:
        if attribute['builtIn'] and attribute['name'] == 'Phone':
            phone_id = attribute['id']
            break

    mappings = [
        {
            'scimAttributeName': 'phoneNumbers[type eq "work"]',
            'builtIn': True,
            'attributeId': phone_id,
            'attributeName': 'Phone',
            'op': 'remove'
        }
    ]
    response = britive.identity_providers.scim_attributes.update_mapping(
        identity_provider_id=cached_identity_provider['id'],
        mappings=mappings
    )
    assert response is None
    idp = britive.identity_providers.get(identity_provider_id=cached_identity_provider['id'])
    assert 'userAttributeScimMappings' in idp.keys()
    assert isinstance(idp['userAttributeScimMappings'], list)
    mappings = idp['userAttributeScimMappings']
    assert 'Phone' not in [m['attributeName'] for m in mappings]


def test_configure_mfa(cached_identity_provider):
    with pytest.raises(exceptions.InvalidRequest) as e:
        response = britive.identity_providers.configure_mfa(
            identity_provider_id=cached_identity_provider['id'],
            root_user=False,
            non_root_user=True
        )
    assert 'E1001 - MFA can only be enabled on default identity provider' in str(e)


def test_signing_certificate():
    cert = britive.identity_providers.signing_certificate()
    assert isinstance(cert, str)
    assert '-----BEGIN CERTIFICATE-----' in cert


def test_set_metadata(cached_identity_provider):
    response = britive.identity_providers.set_metadata(
        identity_provider_id=cached_identity_provider['id'],
        metadata_xml=britive.saml.metadata()
    )
    assert isinstance(response, dict)
    assert 'certificateDn' in response.keys()
    assert response['certificateDn'] == f'CN={britive.tenant.split(".")[0]}'


def test_delete(cached_identity_provider):
    response = britive.identity_providers.delete(identity_provider_id=cached_identity_provider['id'])
    assert response is None
    cleanup('identity-provider')
    cleanup('scim-token')
