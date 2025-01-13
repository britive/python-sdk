# Change Log (v2.8.1+)

## v3.2.0-beta.0 [2025-01-13]

__What's New:__

* Reorganized codebase to align with UI orginizational structure.
* Decoupled `my_requests` and `my_approvals` from `my_access`.
* Added `brokers` and `pools` functionality for `access_broker`.
* Added `firewall` settings functionality.
* Added Britive `managed_permissions` functionality.
* Britive exceptions by type and error code.
* `my_resources` improvements.

__Enhancements:__

* Added `add_favorite` and `delete_favorite` to `my_resources`.
* Added checkout approvals to `my_resources`.
* Added ITSM to checkout approvals.
* Added `(create|list|update|delete)_filter`) to `my_access`.
* Added `response_templates` functionality for `access_broker` credentials.
* Added `request_approval[_by_name]|withdraw_approval_request[_by_name]` to `my_resources`.
* Added `my_access.list` to retrieve access details with new `type=sdk` option.

__Bug Fixes:__

* Fixed missing `param_values` option for resource creation.
* `my_requests.list_approvals` now includes `my_resources` requests.
* Make `get` call in helper method instead `list_approvals`.
* Catch `requests.exceptions.JSONDecodeError` in `_handle_response`.

__Dependencies:__

* `requests >= 2.32.0`

__Other:__

* None

## v3.1.0 [2024-10-07]

__What's New:__

* Added `access_broker` functionality.

__Enhancements:__

* None

__Bug Fixes:__

* Fixed incorrect `if filter` in `secrets_manager`.

__Dependencies:__

* None

__Other:__

* Switched `tox` to install from `requirements.txt`

## v3.0.0 [2024-09-09]

__What's New:__

* Added `access_builder` functionality.
* Added `audit_logs.webhooks` functionality.

__Enhancements:__

* Added `comments` to `my-access.{approve|reject}_request` args.
* Added `filter_expression` to `notification_mediums.list`.
* `notification_mediums.create` now uses `url=...` and `token=...` instead of `connection_parameters`.
* Added `otp` for step up authentication to `my_secrets.{download|view}`.

__Bug Fixes:__

* Fixed issues with some tests and added missing test deletes.

__Dependencies:__

* Dropped support for `python3.7`.
* Dropped `pkg_resources` dependency.

__Other:__

* Removed deprecated `policies.py`.
* Removed deprecated `from_time|to_time`.
* Switched to `ruff` for style linting and code-quality checking.

## v2.25.0 [2024-07-01]

> _NOTE: This will be the last [minor](https://semver.org/#summary) version before 3.0.0_

__What's New:__

* `britive.my_resources` - allow users to list, checkout, and checkin their Cloud PAM Anywhere resources.
* `britive.step_up.authenticate` - allow users to use MFA/TOTP step-up authentication with `britive.my_access.checkout`

__Enhancements:__

* Addition of `gitlab` federation provider
* Addition of `include_tags` on `users.list` and `service_identities.list`

__Bug Fixes:__

* Adding missing `otp` arguments to `my_access`.
* missing `otp` dependency for `tox` testing.

__Dependencies:__

* None

__Other:__

* Added `*_CA_BUNDLE` examples to the docs.
* Add `PYBRITIVE_CA_BUNDLE` to `requests` session if set, introduced in [pybritive (v1.8.0rc2)](https://github.com/britive/python-cli)

## v2.25.0rc5 [2024-06-21]

__What's New:__

* `britive.my_resources` - allow users to list, checkout, and checkin their Cloud PAM Anywhere resources.

__Enhancements:__

* None

__Bug Fixes:__

* missing `otp` dependency for `tox` testing.

__Dependencies:__

* None

__Other:__

* None

## v2.25.0rc4 [2024-06-07]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

* Adding missing `otp` arguments to `my_access`.

__Dependencies:__

* None

__Other:__

* Added `*_CA_BUNDLE` examples to the docs.
* Add `PYBRITIVE_CA_BUNDLE` to `requests` session if set, introduced in [pybritive (v1.8.0rc2)](https://github.com/britive/python-cli)

## v2.25.0rc3 [2024-05-23]

__What's New:__

* `britive.step_up.authenticate` - allow users to use MFA/TOTP step-up authentication with `britive.my_access.checkout`

__Enhancements:__

* None

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.25.0rc2 [2024-05-10]

__What's New:__

* None

__Enhancements:__

* Addition of `include_tags` on `users.list` and `service_identities.list`

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.25.0rc1 [2024-04-22]

__What's New:__

* None

__Enhancements:__

* Addition of `gitlab` federation provider

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.24.0 [2024-04-05]

__What's New:__

* `britive.settings.banner.*` - administer the banner/system announcement
* `britive.banner` - view the banner/system announcement (all end users can view the banner)

__Enhancements:__

* Implement logic to catch and present user-friendly error if a tenant is under maintenance
* `britive.users.minimized_user_details` method to get a summarized set of user attributes given a list of user ids
* `britive.tags.minimized_tag_details` method to get a summarized set of tag attributes given a list of tag ids
* `britive.notification.configure` method changes to support the `memberRules` attribute
* Native [spacelift.io](https://docs.spacelift.io/integrations/cloud-providers/oidc/) OIDC workload federation support
* Add `filter_expression` to listing of system policies/roles/permissions
* Add `secrets_manager.rename()` method
* Add `view=includePolicies` as an option to the listing of profiles

__Bug Fixes:__

* Fix bug related to pagination with system policies/roles/permissions (https://github.com/britive/python-sdk/issues/97)

__Dependencies:__

* Removal of `pkg_resources` dependency

__Other:__

* Remove references to version 1 of profiles as the Britive Platform no longer supports version 1 and all customers have been migrated to version 2
* Updates to the test suite
* Addition of `__version__` in `__init__.py`

## v2.24.0rc5 [2024-04-03]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

* None

__Dependencies:__

* Removal of `pkg_resources` dependency

__Other:__

* Addition of `__version__` in `__init__.py`

## v2.24.0rc4 [2024-04-01]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* Updates to the test suite

## v2.24.0rc3 [2024-03-15]

__What's New:__

* None

__Enhancements:__

* Add `filter_expression` to listing of system policies/roles/permissions
* Add `secrets_manager.rename()` method
* Add `view=includePolicies` as an option

__Bug Fixes:__

* Fix bug related to pagination with system policies/roles/permissions (https://github.com/britive/python-sdk/issues/97)

__Dependencies:__

* None

__Other:__

* Updates to the test suite

## v2.24.0rc2 [2024-01-24]

__What's New:__

* None

__Enhancements:__

* Native [spacelift.io](https://docs.spacelift.io/integrations/cloud-providers/oidc/) OIDC workload federation support

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.24.0rc1 [2024-01-18]

__What's New:__

* `britive.settings.banner.*` - administer the banner/system announcement
* `britive.banner` - view the banner/system announcement (all end users can view the banner)

__Enhancements:__

* Implement logic to catch and present user-friendly error if a tenant is under maintenance
* `britive.users.minimized_user_details` method to get a summarized set of user attributes given a list of user ids
* `britive.tags.minimized_tag_details` method to get a summarized set of tag attributes given a list of tag ids
* `britive.notification.configure` method changes to support the `memberRules` attribute

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* Remove references to version 1 of profiles as the Britive Platform no longer supports version 1 and all customers have been migrated to version 2

## v2.23.0 [2023-11-07]

__What's New:__

* None

__Enhancements:__

* Support for extending a checked out profile via `my_access.extend_checkout` and `my_access.extend_checkout_by_name`

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.23.0rc1 [2023-11-03]

__What's New:__

* None

__Enhancements:__

* Support for extending a checked out profile via `my_access.extend_checkout` and `my_access.extend_checkout_by_name`
*
__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.22.0 [2023-10-12]

__What's New:__

* None

__Enhancements:__

* Support additional policy condition format. Historically only "stringified" JSON was supported by the Britive backend. Now standard JSON is supported and this SDK will now optionally offer to convert the policy condition block to a python dictionary.

__Bug Fixes:__

* Enhanced error handling when a secret or node/path in secrets manager does not exist
* Fixed bug related to AWS federation provider when a tenant was not provided via the BRITIVE_TENANT environment variable

__Dependencies:__

* None

__Other:__

* None

## v2.21.0 [2023-09-15]

__What's New:__

* None

__Enhancements:__

* Support for `environment_association` in `profiles.list`
* Support for `summary` parameter on `profiles.get`

__Bug Fixes:__

* Fixes a bug that will re-request access to a secret instead of raising an exception that the secret request was denied.
* Fixes service identity tokens due to some changes in the way they are generated now that service identity workload federation is supported.
* Fixes a bug with `profiles.update` which was not including all the proper fields in the update request.

__Dependencies:__

* None

__Other:__

* Updates to the test suite.

## v2.20.1 [2023-06-26]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

* Properly handle situation when a user requests approval to checkout a profile but there is already an approved request for that same profile.

__Dependencies:__

* None

__Other:__

* None

## v2.20.0 [2023-06-14]

__What's New:__

* Support for profile permission constraints.

__Enhancements:__

* Support multiple notification mediums for an approval policy condition.

__Bug Fixes:__

* None

__Dependencies:__

* Resolve dependabot alert for `requests` - [security/dependabot/1](https://github.com/britive/python-sdk/security/dependabot/1)

__Other:__

* None

## v2.19.0 [2023-05-09]

__What's New:__

* Added `workload.scim_user` for managed workload identity federation for SCIM users.
* Added `my_access.approve_request`, `my_access.reject_request`, and `my_access.list_approvals`.

__Enhancements:__

* Modified the way in which workload identity providers are associated with service identities.
* Added `date_schedule` and `days_schedule` to the various policy `build` methods.

__Bug Fixes:__

* Addressed race condition in `my_access.checkout` if multiple processes (running as the same user) attempt to check out the same profile for the same environment at the same time

__Dependencies:__

* None

__Other:__

* None

## v2.18.0 [2023-03-27]

__What's New:__

* Support for tag membership rules.

__Enhancements:__

* Allow the creation of external tags (tags associated with an identity provider) using a non-SCIM identity.

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.17.0 [2023-03-14]

__What's New:__

* Workload API coverage (create workload federation identity providers and map to service identities) `workload`
* System Policies coverage `system.policies`
* System Roles coverage `system.roles`
* System Permissions coverage `system.permissions`

__Enhancements:__

* Add custom attribute coverage to users and service identities

__Bug Fixes:__

* None

__Dependencies:__

* For dev/test removed the pin on `pytest` which was causing issues with newer versions of python

__Other:__

* None

___DEPRECATION NOTICE___

__`policies.py`__

This python file only holds one method `build`. The remainder of the system policy logic has been created
in `system.policies` so as not to cause confusion with secrets manager and profile policies.

In the next major release, `policies.py` will be retired. As of release `2.17.0` the `polices.build` method
simply calls `system.policies.build`.

## v2.16.0 [2023-03-02]

__What's New:__

* Natively support Azure Managed Identity OIDC authentication for workload federation.

__Enhancements:__

* None

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.15.1 [2023-02-16]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

* Added missing API call `profiles.get_scopes()`

__Dependencies:__

* None

__Other:__

* None

## v2.15.0 [2023-02-06]

__What's New:__

* Added two new APIs for managing single environment scope changes for a profile
  * `profiles.add_single_environment_scope()`
  * `profiles.remove_single_environment_scope()`

__Enhancements:__

* None

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.14.2 [2023-01-27]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

* In `poilicies.build()` properly handle when lists are empty

__Dependencies:__

* None

__Other:__

* None

## v2.14.1 [2023-01-24]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

* In `profile.poilicies.build()` support the now available `validFor` approval parameter via method parameter `access_validity_time`.

__Dependencies:__

* None

__Other:__

* None

## v2.14.0 [2023-01-18]

__What's New:__

* Added Bitbucket as an OIDC federation provider so that the needed logic for authenticating to Britive via Bitbucket pipelines is abstracted away from the caller.

__Enhancements:__

* None

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.13.0 [2023-01-06]

__What's New:__

* Ability to pass a callback function to the following `my_access` methods which will report progress of the process.
  * `checkout`
  * `checkout_by_name`
  * `request_approval`
  * `request_approval_by_name`

__Enhancements:__

* None

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.12.4 [2023-01-04]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

> ___NOTE:___  This is a pre-release feature. It is being published in anticipation of upcoming features being released to production. This functionality will not yet work in production environments.

* Properly handle use case of long term (IAM User) vs. temporary credentials (AssumeRole/Federation) in the AWS Federation Provider

__Dependencies:__

* None

__Other:__

* None

## v2.12.3 [2022-12-12]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

* Fix bug when catching JSON decode exceptions when decoding `requests` response - catching the more generic `ValueError` instead of a specific JSON decode error

> ___NOTE:___  This is a pre-release feature. It is being published in anticipation of upcoming features being released to production. This functionality will not yet work in production environments.

* Remove port from tenant name in the AWS provider

__Dependencies:__

* None

__Other:__

* Allow disabling TLS/SSL verification for local development work by setting environment variable `export BRITIVE_NO_VERIFY_SSL=true`

## v2.12.2 [2022-11-28]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

> ___NOTE:___  This is a pre-release feature. It is being published in anticipation of upcoming features being released to production. This functionality will not yet work in production environments.

* Fix issue with AWS provider when injecting the tenant name into the AWS sigv4 signed request

__Dependencies:__

* None

__Other:__

* None

## v2.12.1 [2022-11-17]

__What's New:__

* None

__Enhancements:__

> ___NOTE:___  This is a pre-release feature. It is being published in anticipation of upcoming features being released to production. This functionality will not yet work in production environments.

* Allow caller to specify duration/expiration time of tokens generated by the AWS federation provider

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.12.0 [2022-11-16]

__What's New:__

> ___NOTE:___  This is a pre-release feature. It is being published in anticipation of upcoming features being released to production. This functionality will not yet work in production environments.

* Support for workload identity federation providers

__Enhancements:__

* None

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.11.2 [2022-11-01]

__What's New:__

* None

__Enhancements:__

* Reduce number of API calls required to checkout a profile

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.11.1 [2022-10-24]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

* Allow local machine DNS resolution (e.g. /etc/hosts) for tenant URL check

__Dependencies:__

* None

__Other:__

* None

## v2.11.0 [2022-10-18]

__What's New:__

* Support for Secrets Manager APIs
  * Vaults
  * Password Policies
  * Secrets
  * Policies
  * Static Secret Templates
  * Resources
  * Folders
* Support for Notification Medium APIs

__Enhancements:__

* Allow the use of a port number in a tenant URL

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.10.0 [2022-10-06]

__What's New:__

* None

__Enhancements:__

* Allow for non `*.britive-app.com` tenants. Default to `britive-app.com` if no valid URL is provided (for backwards compatibility)

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.9.0 [2022-09-30]

__What's New:__

* Exponential backoff logic added to all API calls.

__Enhancements:__

* Add `filter_expression` to `britive.reports.run()` to allow filtering the results as required by the caller.

__Bug Fixes:__

* None

__Dependencies:__

* None

__Other:__

* None

## v2.8.1 [2022-09-22]

__What's New:__

* None

__Enhancements:__

* None

__Bug Fixes:__

* Fixes an issue with `britive.audit_logs.query()` pagination. The last page of results is now included.
* Fixes an issue with `britive.reports.run()` pagination. The last page of results is now included.
* Fixes an issue with `britive.reports.run()` results being truncated to a maximum of 1000 records when `csv=False`. This was due to how the API handles JSON results vs. CSV results. Now the results are always obtained in CSV format from the API and then converted to a list of dictionaries if `csv=False`.

__Dependencies:__

* None

__Other:__

* None
