# Changes

## 2.0.1 (unreleased)

- Declare and test Python 3.15 support: trove classifier and CI test matrix.
  The test suite passes on 3.15.0 without code changes.

- Pin ruff to 0.16.7 in the QA workflow instead of running unpinned
  `uvx ruff`, so ruff releases no longer change CI behavior on unrelated PRs.
  Newer ruff also formats Python code blocks in Markdown; one plan document
  is reformatted accordingly. Part of the ecosystem-wide alignment
  [bluedynamics/plone-pgcatalog#217](https://github.com/bluedynamics/plone-pgcatalog/issues/217).

## 2.0.0 (2026-04-21)

- **Breaking:** Dropped the `portal_registry.__class__` swap approach. Activation
  is now driven by an import-time monkey-patch on
  `plone.registry.registry.Registry.__getitem__` / `.get`, conditional on the
  presence of `PLONE_REGISTRY_*` environment variables.
- **Breaking:** Removed `setuphandlers.install` / `setuphandlers.uninstall` and
  the corresponding GenericSetup import steps.
- **Breaking:** Removed the `plone.registryfromenviron:uninstall` profile. The
  `default` profile is kept as an empty no-op for dependency-chain compatibility.
- **Compat:** `plone.registryfromenviron.registry.EnvOverrideRegistry` remains
  as an alias for `plone.registry.registry.Registry` so v1.x ZODB pickles that
  reference the symbol continue to load.
- **Upgrade path:** added a GenericSetup upgrade step (1 → 2) that, on click in
  the Plone Add-ons control panel, re-pickles the site root (dropping stale
  `EnvOverrideRegistry` class references) and unregisters the addon from the
  "Installed" list. Runtime activation remains env-var-driven; the step only
  tidies up ZODB and the UI.
- Fixed [issue #1](https://github.com/bluedynamics/plone-registryfromenviron/issues/1):
  class-swap did not persist reliably across ZODB connections because the class
  reference is cached in the parent object's pickle. The new approach avoids
  persistence entirely — overrides are a process-level concern.

## 1.0.1

## 1.0.0

- Initial implementation.
