# Britive Python SDK

Python client for the [Britive API](https://docs.britive.com/apidocs).

The SDK provides Python methods for Britive APIs. It generally passes values to the API for validation, but some methods
combine related API operations or normalize responses for Python callers.

This package supports Python versions `>= 3.10`.

## Installation

```sh
pip install britive
```

To install the current source from GitHub instead of PyPI, run:

```sh
pip install "git+https://github.com/britive/python-sdk.git"
```

## Documentation

Method docstrings describe parameters, return values, and API-specific behavior.

Official API documentation can be found here: [Britive API Documentation](https://docs.britive.com/apidocs).

## Authentication

The SDK accepts Britive API tokens, temporary bearer tokens, and workload federation tokens. Provide an API or bearer
token in one of these ways:

1. Passed directly into the class constructor.
2. Injected as an environment variable into the execution context where this package is being run.

The environment variable name is `BRITIVE_API_TOKEN`.

To source a workload federation token, pass `token_federation_provider` to the `Britive` constructor. Supported
providers include AWS, Azure managed identities, Bitbucket Pipelines, GCP, GitHub Actions, GitLab, and Spacelift.

Every token authenticates against a specific Britive tenant. Provide the tenant in one of these ways:

1. Passed directly into the `Britive` class constructor.
2. Injected as an environment variable into the execution context where this package is being run.

The environment variable name is `BRITIVE_TENANT`.

> _In order to obtain the tenant name, reference the Britive URL used to log into the UI._
> _If the URL is `https://example.britive-app.com` then the tenant name will be `example`._

## Pagination

All pagination is handled by the package. The caller will never have to deal with paginated responses.

## Assumptions

* The caller has access to an active Britive tenant.
* The caller has a token for a user, service identity, or workload.
* No assumptions are made about the operating system or file system.
* The SDK does not persist responses unless a method accepts and receives an output file, such as
  `audit_logs.logs.download_csv(output_file=...)`.

## Resource Coverage

The SDK includes clients for these main Britive areas:

* Access Broker
* API tokens
* Application management, including applications, profiles, accounts, permissions, and scans
* Audit logs and audit log webhooks
* Global settings, including notification mediums, firewall settings, and ITSM
* Identity management, including users, service identities, AI identities, tags, and identity providers
* My Access, My Approvals, My Requests, My Resources, and My Secrets
* Reports
* Secrets Manager
* Security, including SAML, security policies, active sessions, and step-up authentication
* System roles, policies, permissions, consumers, and actions
* Workflows, notifications, and tasks

## Proxies

The SDK uses Python [`requests`](https://github.com/psf/requests) to communicate with the Britive API. Configure an HTTP
proxy through environment variables supported by `requests`.

* HTTP proxies will be set via environment variables.
  * `HTTP_PROXY`
  * `HTTPS_PROXY`
  * `NO_PROXY`
  * `http_proxy`
  * `https_proxy`
  * `no_proxy`

> _Standard HTTP proxy URLs should be utilized._
>
> _Examples:_
>
> * _Unauthenticated Proxy: `http://internalproxy.domain.com:8080`_
> * _Authenticated Proxy: `http://user:pass@internalproxy.domain.com:8080`_

## Custom TLS Certificates

Configure custom TLS certificates through environment variables supported by `requests`.

* Certificate bundles can be set via environment variables.
  * `REQUESTS_CA_BUNDLE`
  * `CURL_CA_BUNDLE` _(used as a fallback)_
  * `PYBRITIVE_CA_BUNDLE` _(specific to the Britive Python SDK)_

> _The values of these environment variables must be a path to a directory of certificates or a specific certificate._
>
> _Example:_
> _`/path/to/certfile`_

### Platform Examples

#### Linux/macOS

```sh
export REQUESTS_CA_BUNDLE="/usr/local/corp-proxy/cacert.pem"
```

#### Windows

##### PowerShell

```pwsh
$env:REQUESTS_CA_BUNDLE = "C:\Users\User\AppData\Local\corp-proxy\cacert.pem"
```

##### Command Prompt

```bat
set "REQUESTS_CA_BUNDLE=C:\Users\User\AppData\Local\corp-proxy\cacert.pem"
```

## Examples

### Importing

This should be the only class that is required for import.

```python
from britive.britive import Britive
```

Optionally, the various exceptions that this package raises can be imported as well, e.g.

```python
from britive import exceptions
```

Then specific exception(s) could be referenced as demonstrated below:

```python
try:
    something()
except exceptions.TokenMissingError:
    handle()
```

### List All Users

```python
from britive.britive import Britive
import json

britive = Britive()  # source needed data from environment variables

print(json.dumps(britive.identity_management.users.list(), indent=2, default=str))
```

### Provide Needed Authentication Information in the Script

```python
from britive.britive import Britive
import json

britive = Britive(tenant='example', token='...') # source token and tenant locally (not from environment variables)

print(json.dumps(britive.identity_management.users.list(), indent=2, default=str))
```

### Create API Token for a Service Identity

```python
from britive.britive import Britive
import json

britive = Britive()  # source needed data from environment variables

print(json.dumps(
    britive.identity_management.service_identity_tokens.create(service_identity_id='abc123'),
    indent=2,
    default=str,
))
```

### Run a Report (JSON and CSV output)

```python
from britive.britive import Britive
import json

britive = Britive()  # source needed data from environment variables

print(json.dumps(britive.reports.run(report_id='abc123'), indent=2, default=str))

with open('file.csv', 'w') as f:
    f.write(britive.reports.run(report_id='abc123', csv=True))
```

### Create an application profile policy

The commands below will create a policy on a profile that allows `user@domain.com` to check out the profile but only if
`approver@domain.com` approves that request within 10 minutes.

```python
from britive.britive import Britive

b = Britive()

policy = b.application_management.profiles.policies.build(
    name='example',
    users=['user@domain.com'],
    approval_notification_medium='Email',
    approver_users=['approver@domain.com'],
    time_to_approve=10
)

b.application_management.profiles.policies.create(profile_id='...', policy=policy)
```
