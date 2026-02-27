# plone.registryfromenviron

Override `plone.registry` values from environment variables.

Plone stores configuration in a persistent registry inside ZODB.
This works well for through-the-web editing, but conflicts with modern deployment practices where configuration is injected via environment variables.

This package bridges that gap, making Plone cloud-native and [12-factor app](https://12factor.net/config) friendly:
the same Plone image can run in development, staging and production with different settings -- controlled entirely by environment variables, no ZODB changes needed.

## How it works

At install time, the package swaps the `portal_registry` object's class to a subclass that checks environment variables **before** falling back to ZODB-stored values.
All existing registry data is preserved.
No monkey-patching -- standard Python subclassing with `super()`.

## Installation

Install the package and apply the GenericSetup profile `plone.registryfromenviron:default` (e.g. via Plone's Add-on control panel).

To uninstall, apply the `plone.registryfromenviron:uninstall` profile.
This reverts `portal_registry` to the base class.

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

- Environment variables are scanned **once at process startup**.
  Changes require a restart.
- Overrides are **read-only** -- writes via the registry API go to ZODB, but reads always return the env value.
- Only **existing** registry keys can be overridden (the field definition is needed for type coercion).
- Invalid values or unknown keys are logged and silently skipped (ZODB value is used as fallback).

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
