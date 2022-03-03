from .cache import *  # will also import some globals like `britive`


def test_settings():
    settings = britive.saml.settings()
    assert isinstance(settings, dict)
    assert 'issuer' in settings.keys()
    assert 'id' in settings.keys()
    assert 'signInUrl' in settings.keys()
    assert 'signOutUrl' in settings.keys()
    assert 'x509CertExpirationDate' in settings.keys()
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

