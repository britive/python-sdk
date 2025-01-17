# Deprecation Notices

This document holds the items which are deprecated and/or warrant specific call out with each major release.


## Moved methods in `v4.0.0`

### `my_access` methods have moved:

| Old location                           | New location                                  |
| -------------------------------------- | --------------------------------------------- |
| `my_access.approval_request_status`    | `my_requests.approval_request_status`         |
| `my_access.approve_request`            | `my_approvals.approve_request`                |
| `my_access.list_approvals`             | `my_approvals.list`                           |
| `my_access.reject_request`             | `my_approvals.reject_request`                 |

### `britive` methods have moved:

| Old location                           | New location                                  |
| -------------------------------------- | --------------------------------------------- |
| `access_builder`                       | `application_management.access_builder`       |
| `accounts`                             | `application_management.accounts`             |
| `applications`                         | `application_management.applications`         |
| `audit_logs`                           | `audit_logs.logs`                             |
| `environment_groups`                   | `application_management.environment_groups`   |
| `environments`                         | `application_management.environments`         |
| `groups`                               | `application_management.groups`               |
| `identity_attributes`                  | `identity_management.identity_attributes`     |
| `identity_providers`                   | `identity_management.identity_providers`      |
| `notification_mediums`                 | `global_settings.notification_mediums`        |
| `notifications`                        | `workflows.notifications`                     |
| `permissions`                          | `application_management.permissions`          |
| `profiles`                             | `application_management.profiles`             |
| `saml`                                 | `security.saml`                               |
| `scans`                                | `application_management.scans`                |
| `security_policies`                    | `security.security_policies`                  |
| `service_identities`                   | `identity_management.service_identities`      |
| `service_identity_tokens`              | `identity_management.service_identity_tokens` |
| `settings`                             | `global_settings`                             |
| `step_up`                              | `security.step_up_auth`                       |
| `tags`                                 | `identity_management.tags`                    |
| `task_services`                        | `workflows.task_services`                     |
| `tasks`                                | `workflows.tasks`                             |
| `users`                                | `identity_management.users`                   |
| `workload`                             | `identity_management.workload`                |

## Removed in Major Release 3.0.0

### `policies.py` has been removed.

### Policy Condition Attributes `from_time` and `to_time` have been removed.

New time based condition fields `date_schedule` and `days_schedule` provided enhanced functionality.

## Deprecations in Major Release 2.x.x (Retire in Major Release 3.x.x)

### `policies.py`

This python file only holds one method `build`. The remainder of the system policy logic has been created in
`system.policies` so as not to cause confusion with secrets manager and profile policies.

In the next major release, `policies.py` will be retired. As of release `2.17.0` the `polices.build` method simply calls
`system.policies.build`.

### Policy Condition Attributes `from_time` and `to_time`

The following policy `build` method parameters `from_time` and `to_time` are deprecated as of release `2.19.0`. The
parameters are still being accepted and will be converted to the go forward policy condition format.

* `system.polices.build`
* `policies.build`
* `profiles.policies.build`
* `secrets_manager.policies.build`

New time based condition fields `date_schedule` and `days_schedule` provided enhanced functionality. Until the next
major release `from_time` and `to_time` parameters will be mapped into the new condition fields to ensure backwards
compatibility.
