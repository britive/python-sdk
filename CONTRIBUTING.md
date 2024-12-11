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
pytest tests/000-global_settings-01-identity_attributes.py -v
pytest tests/000-global_settings-02-notification_mediums.py -v
pytest tests/000-global_settings-03-banner.py -v
pytest tests/100-identity_management-01-users.py -v
pytest tests/100-identity_management-02-tags.py -v
pytest tests/100-identity_management-03-service_identities.py -v
pytest tests/100-identity_management-04-service_identity_tokens.py -v
pytest tests/100-identity_management-05-identity_providers.py -v
pytest tests/100-identity_management-06-workload.py -v
pytest tests/150-secrets_manager-01-secrets_manager.py -v
pytest tests/200-application_management-01-applications.py -v
pytest tests/200-application_management-02-environment_groups.py -v
pytest tests/200-application_management-03-environments.py -v
pytest tests/200-application_management-04-scans.py -v  # WARNING - this one will take a while since it initiates a real scan
pytest tests/200-application_management-05-accounts.py -v  # NOTE - a scan must first be completed
pytest tests/200-application_management-06-permissions.py -v  # NOTE - a scan must first be completed
pytest tests/200-application_management-07-groups.py -v  # NOTE - a scan must first be completed
pytest tests/200-application_management-08-profiles.py -v
pytest tests/200-application_management-09-access_builder.py -v
pytest tests/250-system-01-policies.py -v
pytest tests/250-system-02-actions.py -v
pytest tests/250-system-03-consumers.py -v
pytest tests/250-system-04-roles.py -v
pytest tests/250-system-05-permissions.py -v
pytest tests/300-workflows-01-task_services.py -v
pytest tests/300-workflows-02-tasks.py -v
pytest tests/300-workflows-03-notifications.py -v
pytest tests/350-access_broker-01-response_templates.py -v
pytest tests/350-access_broker-02-resource_types.py -v
pytest tests/350-access_broker-03-resource_labels.py -v
pytest tests/350-access_broker-04-resource.py -v
pytest tests/350-access_broker-05-resource_permissions.py -v
pytest tests/350-access_broker-06-profiles.py -v
pytest tests/350-access_broker-07-profiles_policies.py -v
pytest tests/350-access_broker-08-permissions.py -v
pytest tests/400-security-01-policies.py -v
pytest tests/400-security-02-saml.py -v
pytest tests/400-security-03-api_tokens.py -v
pytest tests/500-audit_logs-01-logs.py -v
pytest tests/500-audit_logs-02-webhooks.py -v
pytest tests/550-reports-01-reports.py -v
pytest tests/600-britive-01-my_access.py -v
pytest tests/600-britive-02-my_secrets.py -v
pytest tests/600-britive-03-my_requests.py -v
pytest tests/600-britive-04-my_approvals.py -v
pytest tests/999-cleanup-01-delete_all_resources.py -v
```

Or you can simply run `pytest -v` to test everything all at once. The above commands however allow you to halt testing
to fix issues that might arise.
