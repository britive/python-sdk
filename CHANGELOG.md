# Change Log

All changes to the package starting with v2.8.1 will be logged here.

## v2.11.0 [2022-10-18]
#### What's New
* Support for Secrets Manager APIs
  * Vaults
  * Password Policies
  * Secrets
  * Policies
  * Static Secret Templates
  * Resources
  * Folders
* Support for Notification Medium APIs

#### Enhancements
* Allow the use of a port number in a tenant URL

#### Bug Fixes
* None

#### Dependencies
* None

#### Other
* None

## v2.10.0 [2022-10-06]
#### What's New
* None

#### Enhancements
* Allow for non `*.britive-app.com` tenants. Default to `britive-app.com` if no valid URL is provided (for backwards compatibility)

#### Bug Fixes
* None

#### Dependencies
* None

#### Other
* None

## v2.9.0 [2022-09-30]
#### What's New
* Exponential backoff logic added to all API calls.

#### Enhancements
* Add `filter_expression` to `britive.reports.run()` to allow filtering the results as required by the caller.

#### Bug Fixes
* None

#### Dependencies
* None

#### Other
* None

## v2.8.1 [2022-09-22]
#### What's New
* None

#### Enhancements
* None

#### Bug Fixes
* Fixes an issue with `britive.audit_logs.query()` pagination. The last page of results is now included.
* Fixes an issue with `britive.reports.run()` pagination. The last page of results is now included.
* Fixes an issue with `britive.reports.run()` results being truncated to a maximum of 1000 records when `csv=False`. This was due to how the API handles JSON results vs. CSV results. Now the results are always obtained in CSV format from the API and then converted to a list of dictionaries if `csv=False`.

#### Dependencies
* None

#### Other
* None
