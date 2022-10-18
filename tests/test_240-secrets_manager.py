import time
import britive.exceptions
from britive import policies
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
    britive.secrets_manager.vaults.update(cached_vault['id'], description='12345')
    vault = britive.secrets_manager.vaults.get_vault_by_id(cached_vault['id'])
    assert vault['description'] == '12345'


def test_create_folder(cached_folder):
    assert isinstance(cached_folder, dict)


def test_PasswordPolicies_create(cached_PasswordPolicies):
    assert isinstance(cached_PasswordPolicies, dict)


def test_PinPolicies_create(cached_PinPolicies):
    assert isinstance(cached_PinPolicies, dict)


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
    r = str(random.randint(0, 1000000))
    new_name = f"pytestpolicy-{r}"
    britive.secrets_manager.password_policies.update(cached_PasswordPolicies['id'], name=new_name)
    assert britive.secrets_manager.password_policies.get(
        cached_PasswordPolicies['id'])['name'] == new_name


def test_generate_password(cached_PasswordPolicies):
    password = britive.secrets_manager.password_policies.generate_password(
        cached_PasswordPolicies['id'])
    assert isinstance(password, str)


def test_validate_password(cached_PasswordPolicies):
    response = britive.secrets_manager.password_policies.validate(
        cached_PasswordPolicies['id'],
        'testpassword')
    assert response['isPasswordOrPinValid'] is False


def test_secret_create(cached_secret):
    assert isinstance(cached_secret, dict)


def test_secret_get(cached_vault): 
    secret = britive.secrets_manager.secrets.get(
        vault_id=cached_vault['id'],
        path='/', secret_type='secret')[0]
    assert isinstance(secret, dict)


def test_secret_update(cached_secret, cached_vault):
    update = britive.secrets_manager.secrets.update(
        cached_vault['id'],
        cached_secret['path'],
        {'Note' : 'updated test note'}
    )
    assert update is None


def test_policies_list():
    policies = britive.secrets_manager.policies.list()
    assert isinstance(policies, list)
    assert isinstance(policies[0], dict)


def test_policies_create(cached_policy):
    assert isinstance(cached_policy, dict)


def test_static_secret_template_create(cached_static_secret_template):
    assert isinstance(cached_static_secret_template, dict)


def test_static_secret_template_list():
    response = britive.secrets_manager.static_secret_templates.list()
    assert isinstance(response, list)
    assert len(response)>0
    assert isinstance(response[0], dict)


def test_static_secret_template_get(cached_static_secret_template):
    static_secret_template = britive.secrets_manager.static_secret_templates.get(
        cached_static_secret_template['id'])
    assert isinstance(static_secret_template, dict)
    assert cached_static_secret_template['id'] == static_secret_template['id']


def test_static_secret_template_update(cached_static_secret_template):
    britive.secrets_manager.static_secret_templates.update(
        cached_static_secret_template['id'],
        description = 'test desc')
    assert britive.secrets_manager.static_secret_templates.get(
        cached_static_secret_template['id'])['description'] == 'test desc'


def test_resources_get():
    response = britive.secrets_manager.resources.get('/')
    assert isinstance(response, dict)


def test_rotate_keys(cached_vault):
    initial_time = britive.secrets_manager.vaults.get_vault_by_id(cached_vault['id'])['lastRotation']
    britive.secrets_manager.vaults.rotate_keys()
    current_time = britive.secrets_manager.vaults.get_vault_by_id(cached_vault['id'])['lastRotation']
    assert initial_time != current_time
    tries = 0
    while True:
        try:
            if tries >= 30:
                raise Exception('timed out - vault rotation took too long')
            britive.my_secrets.list()
            break
        except exceptions.NoSecretsVaultFound:
            time.sleep(3)
            tries += 1


