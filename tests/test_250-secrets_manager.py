from .cache import *  # will also import some globals like `britive`

def test_create_vault(cached_vault):
    assert isinstance(cached_vault, dict)

def test_list_vault(cached_vault):
    response = britive.secrets_manager.vaults.list()
    assert isinstance(response, dict)
    assert len(response) > 0

def test_get_vault(cached_vault):
    vault = britive.secrets_manager.vaults.get_vault_by_id(cached_vault['id'])
    assert isinstance(vault, dict)
    assert vault['id'] == cached_vault['id']

def test_update_vault(cached_vault):
    britive.secrets_manager.vaults.update(cached_vault['id'], name="12345")
    vault = britive.secrets_manager.vaults.get_vault_by_id(cached_vault['id'])
    assert vault['name'] == '12345'

def test_create_folder(cached_folder):
    assert isinstance(cached_folder, dict)

def test_PasswordPolicies_create(cached_PasswordPolicies):
    assert isinstance(cached_PasswordPolicies, dict)

def test_PasswordPolicies_get(cached_PasswordPolicies):
    pwdpolicy = britive.secrets_manager.password_policies.get(cached_PasswordPolicies['id'])
    assert isinstance(pwdpolicy, dict)
    assert pwdpolicy['id'] == cached_PasswordPolicies['id']

def test_PasswordPolicies_list():
    response = britive.secrets_manager.password_policies.list()
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)

def test_PasswordPolicies_update(cached_PasswordPolicies):
    britive.secrets_manager.password_policies.update(cached_PasswordPolicies['id'], name="12345")
    assert britive.secrets_manager.password_policies.get(cached_PasswordPolicies['id'])['name'] == '12345'

def test_secret_create(cached_secret):
    assert isinstance(cached_secret, dict)

"""
def test_secret_get(cached_secret, cached_vault):
    secret = britive.secrets_manager.secrets.get(cached_vault['id'], cached_secret['path'])
    assert isinstance(secret, dict)
"""

def test_secret_update(cached_secret, cached_vault):
    britive.secrets_manager.secrets.update(cached_vault['id'], cached_secret['path'], {'Note' : "updated test note"})

def test_static_secret_template_create(cached_static_secret_template):
    assert isinstance(cached_static_secret_template, dict)

def test_static_secret_template_list():
    response = britive.secrets_manager.static_secret_templates.list()
    assert isinstance(response, list)
    assert len(response)>0
    assert isinstance(response[0], dict)

def test_static_secret_template_get(cached_static_secret_template):
    static_secret_template = britive.secrets_manager.static_secret_templates.get(cached_static_secret_template['id'])
    assert isinstance(static_secret_template, dict)
    assert cached_static_secret_template['id'] == static_secret_template['id']

def test_static_secret_template_update(cached_static_secret_template):
    britive.secrets_manager.static_secret_templates.update(cached_static_secret_template['id'], description = "test desc")
    assert britive.secrets_manager.static_secret_templates.get(cached_static_secret_template['id'])['description'] == "test desc"
    






