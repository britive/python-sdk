> __TODO:__ _add structure/development/convention sections._

# Python Britive SDK

This repo will hold the python code that wraps the Britive API so downstream python applications/scripts
can consume a native Python library.

## Python Version Support

_CURRENT SUPPORTED VERSION(S):_ `>= 3.8`

We use [typing](https://docs.python.org/3/library/typing.html) and dictionary unpacking, e.g. `{**dict1, **dict2}`,
which requires Python 3.5 or greater.

## Production Use

Install requirements.

```sh
pip install -r requirements.txt
```

## Local Install

```sh
pip install --editable .
```

## Build

* Update version in `src/britive/__init__.py`
* Push code to GitHub
* Cut a new PR and merge when appropriate
* Run below commands

```sh
python -m pip install --upgrade build
python -m build
```

* Cut a new release in GitHub with the version tag
* Add the assets from `dist` directory to the release

We will now have a new `./dist` directory containing a `.tar.gz` tarball and `whl` wheel. The wheel is considered a
"built distribution" meaning it is compiled for various OSes and architectures. In our case this is a pure Python
implementation so the wheel is for all OSes and architectures (`-py3-none-any.whl`).

## Github Actions

There are 2 Github Actions in play that publish to PyPI.

1. Trigger off of a push to the `develop` branch -- will deploy to test PyPI.
2. Trigger off of a new release being published -- will deploy to real PyPI.

## Testing

Install requirements.

```sh
pip install -r requirements/dev.txt
```

This library is using `tox` for true package testing. `tox` will install the package distribution in a virtual
environment and then run the tests (using `pytest`) inside of that clean environment. This ensures that the packaging
process itself is also working as expected.

To run just execute `tox` on the command line or if you want to clean the environment `tox -r` which will rebuild the
entire virtualenv. There are some issues with pytest caching that have been found so cleaning the virtualenv helps clear
that up.

`pytest` is being used to test the SDK. Run the following commands in order to test the full library.

These below tests/commands should only be run during local development when iterating quickly (more like unit testing).
`tox` should be used when possible to test the full end-to-end process (more like integration testing).

If you do want to run these outside of `tox` you will need to set this environment variable so that we can do some
`PATH` magic in `tests/__init__.py`.

```sh
export BRITIVE_UNIT_TESTING=true
```

You will also need other environment variables.

* The AWS account that will be used to create test applications/environments/etc. This is being added as an environment
variable, so it is not hardcoded into the tests and stored in the repo as a result.

_NOTE:_ this AWS account will need 2 IAM resources.

* Identity Provider: name of _BritivePythonApiWrapperTesting-\{tenant\}_
* Role: name of _britive-integration-role-\{tenant\}_

where _\{tenant\}_ is the lowercase tenant and is also what is set below in the `BRITIVE_TENANT` env var

```sh
export BRITIVE_API_TOKEN=...
export BRITIVE_TENANT=...
export BRITIVE_TEST_ENV_ACCOUNT_ID=<12 digit AWS account id>
```

Optionally you can set 2 variables which will override the IDP and Integration Role names from above.

```sh
export BRITIVE_IDP_NAME_OVERRIDE=...
export BRITIVE_INTEGRATION_ROLE_NAME_OVERRIDE=...
```

If you want to skip running a scan (and waiting a long time for the results) you can set

```sh
export BRITIVE_TEST_IGNORE_SCAN=true
```

And then all the API calls that are reliant on a scan to occur will be ignored. This may be useful when you just want
to an internal end-to-end process vs. integrating with a cloud service provider.

Then run these in order or as required.

```sh
pytest tests/005-identity_attributes.py -v
pytest tests/010-users.py -v
pytest tests/020-tags.py -v
pytest tests/030-service_identities.py -v
pytest tests/040-service_identity_tokens.py -v
pytest tests/050-applications.py -v
pytest tests/060-environment_groups.py -v
pytest tests/070-environments.py -v
pytest tests/080-scans.py -v  # WARNING - this one will take a while since it initiates a real scan
pytest tests/090-accounts.py -v  # NOTE - a scan must first be completed
pytest tests/100-permissions.py -v  # NOTE - a scan must first be completed
pytest tests/110-groups.py -v  # NOTE - a scan must first be completed
pytest tests/130-profiles.py -v
pytest tests/140-task_services.py -v
pytest tests/150-tasks.py -v
pytest tests/160-security_policies.py -v
pytest tests/170-saml.py -v
pytest tests/180-api_tokens.py -v
pytest tests/190-audit_logs.py -v
pytest tests/200-reports.py -v
pytest tests/210-identity_providers.py -v
pytest tests/215-workload.py -v
pytest tests/220-my_access.py -v
pytest tests/230-notifications.py -v
pytest tests/240-secrets_manager.py -v
pytest tests/250-my_secrets.py -v
pytest tests/260-notification_mediums.py -v
pytest tests/270-system_policies.py -v
pytest tests/280_system_actions.py -v
pytest tests/290_system_consumers.py -v
pytest tests/300-system_roles.py -v
pytest tests/310-system_permissions.py -v
pytest tests/320-settings_banner.py -v
pytest tests/330-response_templates.py -v
pytest tests/340-resource_types.py -v
pytest tests/350-resource_labels.py -v
pytest tests/360-resource.py -v
pytest tests/370-resource_permissions.py -v
pytest tests/380-access_broker_profiles.py -v
pytest tests/390-access_broker_profiles_policies.py -v
pytest tests/400-access_broker_permissions.py -v
pytest tests/990-delete_all_resources.py -v
```

Or you can simply run `pytest -v` to test everything all at once. The above commands however allow you to halt testing
to fix issues that might arise.
