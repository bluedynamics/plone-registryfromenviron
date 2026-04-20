# plone.registryfromenviron

Override `plone.registry` values from environment variables.

Plone stores configuration in a persistent registry inside ZODB.
This works well for through-the-web editing, but conflicts with modern deployment practices where configuration is injected via environment variables.

This package bridges that gap, making Plone cloud-native and [12-factor app](https://12factor.net/config) friendly:
the same Plone image can run in development, staging and production with different settings -- controlled entirely by environment variables, no ZODB changes needed.

## How it works

At import time, the package scans `os.environ` for `PLONE_REGISTRY_*` variables.
If any are present, it patches `plone.registry.registry.Registry.__getitem__` and `.get` so that reads consult the env-var values first, falling back to ZODB when a key is not overridden.
If no matching env vars are set, the package is a silent no-op with zero runtime cost.

All existing registry data is preserved — overrides are read-only and never written to ZODB.

## Installation

Add the package to your Plone image / buildout / Python environment.
That's it — no GenericSetup profile needs to be applied and nothing is written to ZODB.

The package ships with a `plone.registryfromenviron:default` profile for backwards compatibility with 1.x, but it is an empty no-op.
You may leave it listed as a dependency in your own `metadata.xml` without any effect.

"Uninstalling" means removing the package from the deployment (and restarting the processes).
There is no uninstall profile in 2.0.

## Environment variable format

```
PLONE_REGISTRY_<registry_key>=<value>
```

Registry keys use dots (e.g. `plone.smtp_host`).
Since dots are not allowed in environment variable names, replace each `.` with `__` (double underscore).
Single underscores are preserved as-is.

### Examples

```bash
# plone.smtp_host = "mail.example.com"
export PLONE_REGISTRY_plone__smtp_host=mail.example.com

# plone.app.theming.interfaces.IThemeSettings.enabled = False
export PLONE_REGISTRY_plone__app__theming__interfaces__IThemeSettings__enabled=false

# plone.cachepurging.interfaces.ICachePurgingSettings.cachingProxies = ["http://varnish:8080"]
export PLONE_REGISTRY_plone__cachepurging__interfaces__ICachePurgingSettings__cachingProxies='["http://varnish:8080"]'
```

## Type coercion

Values are automatically coerced based on the existing registry record's field type:

| Field type | Env value example | Result |
|---|---|---|
| Bool | `true`, `1`, `yes`, `on` | `True` |
| Bool | `false`, `0`, `no`, `off` | `False` |
| Int | `42` | `42` |
| Float | `3.14` | `3.14` |
| TextLine / Text | `hello` | `"hello"` |
| List | `["a", "b"]` | `["a", "b"]` |
| Tuple | `["a", "b"]` | `("a", "b")` |
| Set | `["a", "b"]` | `{"a", "b"}` |
| Dict | `{"key": "val"}` | `{"key": "val"}` |

Collection and dict values use JSON syntax.

## Behavior

- Environment variables are scanned **once at process startup**. Changes require a restart.
- Activation is automatic: if `PLONE_REGISTRY_*` variables are present, the patch is applied at first import. If not, nothing happens.
- Overrides are **read-only** — writes via the registry API still go to ZODB, but subsequent reads for overridden keys return the env value.
- Only **existing** registry keys can be overridden (the field definition is needed for type coercion).
- Invalid values or unknown keys are logged and silently skipped (ZODB value is used as fallback).
- **Known limitation:** direct access via `registry.records['key'].value` bypasses the override, the same as in 1.x. Use `registry['key']`, `registry.get('key')`, or a `RecordsProxy` (all go through the patched read path).

## Upgrading from 1.x

Version 2.0 drops the `portal_registry.__class__` swap approach (see [issue #1](https://github.com/bluedynamics/plone-registryfromenviron/issues/1) for the root-cause analysis).

For operators upgrading from 1.x:

- **Deploy 2.0, then click "Upgrade" once in the Plone Add-ons control panel.** A GenericSetup upgrade step (1 → 2) clears any stale `EnvOverrideRegistry` class references from the site root and unregisters the addon from the "Installed" list of the control panel. Runtime activation is driven by env vars; the click only tidies up ZODB and the UI. If you do nothing, the addon keeps working correctly — the cleanup is cosmetic.
- **No uninstall step needed.** Stop setting `PLONE_REGISTRY_*` env vars to deactivate, or remove the package from the deployment.
- **The `plone.registryfromenviron:uninstall` profile is gone.** If your automation calls it, remove the call — it's a no-op.
- **Activation is now import-driven, not install-step-driven.** Every pod picks up the behavior immediately on startup; no per-site install run is required anymore.

## Source Code and Contributions

The source code is managed in a Git repository, with its main branches hosted on GitHub.
Issues can be reported there too.

We'd be happy to see many forks and pull requests to make this package even better.
We welcome AI-assisted contributions, but expect every contributor to fully understand and be able to explain the code they submit.
Please don't send bulk auto-generated pull requests.

Maintainers are Jens Klein, Johannes Raggam and the BlueDynamics Alliance developer team.
We appreciate any contribution and if a release on PyPI is needed, please just contact one of us.
We also offer commercial support if any training, coaching, integration or adaptations are needed.

- [CHANGES.md](https://github.com/bluedynamics/plone-registryfromenviron/blob/main/CHANGES.md) -- changelog

## License

GPL-2.0-only
