# Britive Python API Wrapper

Pure Python implementation for interacting with the Britive API.

This package aims to wrap the Britive API for use in Python. For the most part it is a simple wrapper (sending
potentially bad parameters to the API) but there are a couple of places where liberties were taken to enhance
the developer/end user experience. Some APIs may also be combined into one Python method with a parameter if and
where it makes more sense to present the API that way.

This package supports Python 3.7 and higher.


## Documentation

Each public method is documented with a docstring which provides details on what the method does, the parameters the
method accepts, and details about what is returned from the method.

Official API documentation can be found at https://docs.britive.com/v1/docs/en/overview-britive-apis.

## Authentication

Authentication is handled solely via API tokens. The token can be presented in one of two methods.

* Passed directly into the `Britive` class constructor (not preferred as credentials have the potential to be saved into
   a code repository).
* Injected as an environment variable into the execution context where this package is being run. The
   environment variable name must be `BRITIVE_API_TOKEN`.

All Britive API tokens are authenticated against a specific Britive tenant. The name of the tenant must be presented
in one of two methods.

* Passed directly into the `Britive` class constructor.
* Injected as an environment variable into the execution context where this package is being run. The
   environment variable name must be `BRITIVE_TENANT`.

In order to obtain the tenant name, reference the Britive URL used to log into the UI. If the URL is
https://example.britive-app.com then the tenant name will be `example`.

## Pagination

All pagination is handled by the package. The caller will never have to deal with paginated responses.

## Assumptions

* The caller has access to an active Britive tenant.
* The caller has been granted an API token and/or has the ability to generate an API token. This can be either for
    a User or Service Identity.
* No assumptions are made about the operating system or file system. Nothing is persisted to disk. The end user 
    must persist responses to disk if and when that is required.

## Resource Coverage

The following Britive resources are supported with full CRUDL operations where appropriate, and additional actions
where they exist.

* Accounts
* API Tokens (for Users)
* Applications
* Audit Logs
* Environment Groups
* Environment
* Groups (associated with an application/environment)
* Accounts (associated with an application/environment)
* Permissions (associated with an application/environment)
* Identity Attributes
* Identity Providers
* My Access (access granted to the given identity (user or service))
* Notifications
* Profiles
* Reports
* SAML Settings
* Scans
* Security Policies
* Service Identities
* Service Identity Tokens
* Tags (aka User Tags)
* Task Services
* Tasks
* Users

## Examples

### Importing

This should be the only class that is required for import.
~~~python
from britive.britive import Britive
~~~

Optionally the various exceptions that this package raises can be imported as well.
~~~python
from britive import exceptions
~~~

Then a specific exception could be referenced as 
~~~python
try:
    something()
except exceptions.TokenMissingError():
    handle()
~~~


### List All Users
~~~python
from britive.britive import Britive
import json

britive = Britive()  # source needed data from environment variables

print(json.dumps(britive.users.list(), indent=2, default=str))
~~~

### Provide Needed Authentication Information in the Script
~~~python
from britive.britive import Britive
import json

britive = Britive(tenant='example', token='abcd1234') 

print(json.dumps(britive.users.list(), indent=2, default=str))
~~~


### Create API Token for a Service Identity
~~~python
from britive.britive import Britive
import json

britive = Britive()  # source needed data from environment variables

print(json.dumps(britive.service_identity_tokens.create(service_identity_id='abc123'), indent=2, default=str))
~~~

### Run a Report (JSON and CSV output)
~~~python
from britive.britive import Britive
import json

britive = Britive()  # source needed data from environment variables

print(json.dumps(britive.reports.run(report_id='abc123'), indent=2, default=str))

with open('file.csv', 'w') as f:
    f.write(britive.reports.run(report_id='abc123', csv=True))
~~~

