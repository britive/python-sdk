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


def test_password_policies_create(cached_password_policies):
    assert isinstance(cached_password_policies, dict)


def test_pin_policies_create(cached_pin_policies):
    assert isinstance(cached_pin_policies, dict)


def test_password_policies_get(cached_password_policies):
    pwdpolicy = britive.secrets_manager.password_policies.get(cached_password_policies['id'])
    assert isinstance(pwdpolicy, dict)
    assert pwdpolicy['id'] == cached_password_policies['id']


def test_password_policies_list():
    response = britive.secrets_manager.password_policies.list()
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)


def test_password_policies_update(cached_password_policies):
    r = str(random.randint(0, 1000000))
    new_name = f"pytestpolicy-{r}"
    britive.secrets_manager.password_policies.update(cached_password_policies['id'], name=new_name)
    assert britive.secrets_manager.password_policies.get(
        cached_password_policies['id'])['name'] == new_name


def test_generate_password(cached_password_policies):
    time.sleep(5)  # sleep for 5 seconds as I think the password policy update takes a bit to settle down
    password = britive.secrets_manager.password_policies.generate_password(
        cached_password_policies['id'])
    assert isinstance(password, str)


def test_validate_password(cached_password_policies):
    response = britive.secrets_manager.password_policies.validate(
        cached_password_policies['id'],
        'testpassword')
    assert response['isPasswordOrPinValid'] is False


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
        description='test desc')
    assert britive.secrets_manager.static_secret_templates.get(
        cached_static_secret_template['id'])['description'] == 'test desc'


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
        {'Note': 'updated test note'}
    )
    assert update is None

def test_secret_rename(cached_secret, cached_vault):
    name = cached_secret['name']
    rename = britive.secrets_manager.secrets.rename(
        cached_vault['id']
        , cached_secret['path']
        , 'testSecretRename')
    assert rename is None

    new_path_list = cached_secret['path'].split('/')
    new_path_list.pop()
    new_path_list.append('testSecretRename')
    new_path = '/'.join(new_path_list)

    rollback = britive.secrets_manager.secrets.rename(
        cached_vault['id']
        , new_path
        , name)
    assert rollback is None


def test_policies_create(cached_policy):
    assert isinstance(cached_policy, dict)


def test_policies_list():
    sec_policies = britive.secrets_manager.policies.list()
    assert isinstance(sec_policies, list)
    assert isinstance(sec_policies[0], dict)


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
        except exceptions.NotFound:
            time.sleep(3)
            tries += 1


