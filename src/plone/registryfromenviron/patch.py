"""Import-time monkey-patch for plone.registry.registry.Registry.

``lineage.registry.proxy.LineageRegistry`` (subsite registries of
collective.lineage) overrides ``__getitem__`` and ``get``, so it is patched
as well when lineage.registry is installed.
"""

from .environ import _MARKER
from .environ import get_override
from collections.abc import Callable
from plone.registry.registry import Registry

import logging


try:
    from lineage.registry.proxy import LineageRegistry
except ImportError:
    LineageRegistry = None


logger = logging.getLogger(__name__)

_originals: dict[tuple[type, str], Callable] = {}


def _make_getitem(original):
    def __getitem__(self, name):
        value = get_override(self, name)
        if value is not _MARKER:
            return value
        return original(self, name)

    return __getitem__


def _make_get(original):
    def get(self, name, default=None):
        value = get_override(self, name)
        if value is not _MARKER:
            return value
        return original(self, name, default)

    return get


def _targets():
    targets = [Registry]
    if LineageRegistry is not None:
        targets.append(LineageRegistry)
    return targets


def apply_patch():
    """Patch __getitem__ / .get to consult env-var overrides first.

    Patches ``Registry`` and, if installed, ``LineageRegistry``.
    Idempotent: calling twice is a no-op.
    """
    if _originals:
        return
    for cls in _targets():
        _originals[(cls, "__getitem__")] = cls.__getitem__
        _originals[(cls, "get")] = cls.get
        cls.__getitem__ = _make_getitem(cls.__getitem__)
        cls.get = _make_get(cls.get)
        logger.info("%s.%s patched for env-var overrides", cls.__module__, cls.__name__)


def unpatch():
    """Restore the original methods. Safe when not patched."""
    for (cls, name), original in _originals.items():
        setattr(cls, name, original)
    _originals.clear()
