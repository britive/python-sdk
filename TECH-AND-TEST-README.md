# Python Britive API Wrapper

This repo will hold the python code that wraps the Britive API so downstream python applications/scripts
can consume a native Python library.

## Python Version Support
We use `typing` in this package so a requirement is Python 3.5 or greater - https://docs.python.org/3/library/typing.html.
Use of {**dict1, **dict2} exists in profiles.py and that also requires Python 3.5 or greater.
`requests` package will stop supporting 3.6 in 2022 so we should bump to only supporting Python 3.7 and up


## Production Use
Install requirements.

~~~
pip install -r requirements.txt
~~~


## Building

Steps from here: https://packaging.python.org/en/latest/tutorials/packaging-projects/

Inside the existing virtualenv...

~~~
python -m pip install --upgrade build
python -m build
~~~

We will now have a new `/dist` directory containing a `.tar.gz` tarball and `whl` wheel. The wheel is considered
a "built distribution" meaning it is compiled for various OSes and architectures. In our case this is a pure Python
implementation so the wheel is for all OSes and architectures (`-py3-none-any.whl`).



## Testing
Install requirements.

~~~
pip install -r requirements/dev.txt
~~~

This library is using `tox` for true package testing. `tox` will install the package distribution in a virtual
environment and then run the tests (using `pytest`) inside of that clean environment. This ensures that the packaging
process itself is also working as expected.

To run just execute `tox` on the command line or if you want to clean the environment `tox -r` which will
rebuild the entire virtualenv. There are some issues with pytest caching that have been found so cleaning the virtualenv
helps clear that up.

`pytest` is being used to test the API wrapper. Run the following commands in order to test the full library.

These below tests/commands should only be run during local development when iterating quickly (more like unit testing). 
`tox` should be used when possible to test the full end-to-end process (more like integration testing).

If you do want to run these outside of `tox` you will need to set this environment variable so that we can do some
PATH magic in `tests/__init__.py`.

~~~
export BRITIVE_UNIT_TESTING=true
~~~

You will also need to other environment variables.

1. The AWS account that will be used to create test applications/environments/etc. This is being added as an 
environment variable, so it is not hardcoded into the tests and store in the repo as a result.

2. Your Britive user email address - this will be used to find your user ID when the checkout/checkins are performed.

~~~
export BRITIVE_TEST_ENV_ACCOUNT_ID=<12 digit AWS account id>
export BRITIVE_USER_EMAIL=<your email address>
~~~

Then run these in order or as required.

~~~
pytest tests/test_010-users.py -v
pytest tests/test_020-tags.py -v
pytest tests/test_030-service_identities.py -v
pytest tests/test_040-service_identity_tokens.py -v
pytest tests/test_050-applications.py -v
pytest tests/test_060-environment_groups.py -v
pytest tests/test_070-environments.py -v
pytest tests/test_080-scans.py -v  # warning - this one will take a while since it initiates a real scan
pytest tests/test_090-accounts.py -v # note - a scan must first be completed
pytest tests/test_100-permissions.py -v # note - a scan must first be completed
pytest tests/test_110-groups.py -v # note - a scan must first be completed
pytest tests/test_120-identity_attributes.py -v
pytest tests/test_130-profiles.py -v
pytest tests/test_140-task_services.py -v
pytest tests/test_150-tasks.py -v
pytest tests/test_160-security_policies.py -v
pytest tests/test_170-saml.py -v
pytest tests/test_180-api_tokens.py -v
pytest tests/test_190-audit_logs.py -v
pytest tests/test_200-reports.py -v
pytest tests/test_210-identity_providers.py -v
pytest tests/test_220-my_access.py -v
pytest tests/test_230-notifications.py -v

pytest tests/test_990-delete_all_resources.py -v
~~~

Or you can simply run `pytest -v` to test everything all at once. The above commands however allow you to halt
testing to fix issues that might arise.
