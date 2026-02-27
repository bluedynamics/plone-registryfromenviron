"""GenericSetup install/uninstall handlers for plone.registryfromenviron."""

from .registry import EnvOverrideRegistry
from plone.app.registry.registry import Registry as BaseAppRegistry

import logging


log = logging.getLogger(__name__)


def install(context):
    """Swap portal_registry.__class__ to EnvOverrideRegistry."""
    if context.readDataFile("install_marker.txt") is None:
        return
    site = context.getSite()
    registry = getattr(site, "portal_registry", None)
    if registry is None:
        return
    if isinstance(registry, EnvOverrideRegistry):
        log.info("portal_registry is already EnvOverrideRegistry")
        return
    registry.__class__ = EnvOverrideRegistry
    log.info("Swapped portal_registry to EnvOverrideRegistry")


def uninstall(context):
    """Revert portal_registry.__class__ to base Registry."""
    if context.readDataFile("uninstall_marker.txt") is None:
        return
    site = context.getSite()
    registry = getattr(site, "portal_registry", None)
    if registry is None:
        return
    if not isinstance(registry, EnvOverrideRegistry):
        log.info("portal_registry is not EnvOverrideRegistry, nothing to revert")
        return
    registry.__class__ = BaseAppRegistry
    log.info("Reverted portal_registry to base Registry class")
