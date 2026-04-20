"""Import-time monkey-patch for plone.registry.registry.Registry."""

from .environ import _MARKER
from .environ import get_override
from collections.abc import Callable
from plone.registry.registry import Registry

import logging


logger = logging.getLogger(__name__)

_originals: dict[str, Callable] = {}


def _patched_getitem(self, name):
    value = get_override(self, name)
    if value is not _MARKER:
        return value
    return _originals["__getitem__"](self, name)


def _patched_get(self, name, default=None):
    value = get_override(self, name)
    if value is not _MARKER:
        return value
    return _originals["get"](self, name, default)


def apply_patch():
    """Patch Registry.__getitem__ / .get to consult env-var overrides first.

    Idempotent: calling twice is a no-op.
    """
    if _originals:
        return
    _originals["__getitem__"] = Registry.__getitem__
    _originals["get"] = Registry.get
    Registry.__getitem__ = _patched_getitem
    Registry.get = _patched_get
    logger.info("plone.registry.registry.Registry patched for env-var overrides")


def unpatch():
    """Restore the original Registry methods. Safe when not patched."""
    if not _originals:
        return
    Registry.__getitem__ = _originals["__getitem__"]
    Registry.get = _originals["get"]
    _originals.clear()
