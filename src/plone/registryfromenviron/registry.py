"""Backwards-compatibility shim for v1.x.

v1.x persisted ``portal_registry.__class__ = EnvOverrideRegistry`` via a
GenericSetup handler. That approach was fragile (see issue #1) and is gone
in 2.0 — overrides now happen via an import-time monkey-patch on the base
``Registry`` class. See :mod:`plone.registryfromenviron.patch`.

To keep any v1.x ZODB pickle referencing this symbol loadable, the name
resolves to the plain base class. Unpickling produces a regular
``Registry`` instance; the patch applies at call time.
"""

from plone.registry.registry import Registry

EnvOverrideRegistry = Registry
