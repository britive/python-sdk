# Deprecation Notices

This document holds the items which are deprecated and will be retired in the next major release.

## Deprecations in Major Release 2.x.x (Retire in Major Release 3.x.x)

#### `policies.py`

This python file only holds one method `build`. The remainder of the system policy logic has been created
in `system.policies` so as not to cause confusion with secrets manager and profile policies.

In the next major release, `policies.py` will be retired. As of release `2.17.0` the `polices.build` method
simply calls `system.policies.build`. 