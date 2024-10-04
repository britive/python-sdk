from .cache import *  # will also import some globals like `britive`


def test_settings():
    settings = britive.saml.settings()
    assert isinstance(settings, dict)
    assert 'issuer' in settings
    assert 'id' in settings
    assert 'signInUrl' in settings
    assert 'signOutUrl' in settings
    assert 'x509CertExpirationDate' in settings
    settings = britive.saml.settings(as_list=True)
    assert isinstance(settings, list)
    assert len(settings) == 1


def test_metadata():
    metadata = britive.saml.metadata()
    assert isinstance(metadata, str)
    assert 'ds:X509Certificate' in metadata


def test_download():
    certificate = britive.saml.certificate()
    assert isinstance(certificate, str)
    assert '-----BEGIN CERTIFICATE-----' in certificate
