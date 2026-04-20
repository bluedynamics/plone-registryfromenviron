"""GenericSetup upgrade steps for plone.registryfromenviron."""

import logging


logger = logging.getLogger(__name__)

PROFILE_ID = "plone.registryfromenviron:default"


def upgrade_to_2(setup_tool):
    """Clean up after v1 install.

    v1 used a GenericSetup install handler that swapped
    ``portal_registry.__class__``. v2 replaces that with an import-time
    monkey-patch driven by env vars. This step:

    1) Forces re-pickling of the site root so any parent-level class
       references to ``plone.registryfromenviron.registry.EnvOverrideRegistry``
       are rewritten to the plain ``Registry`` (via the 2.0 alias).
    2) Unregisters the profile from the Add-ons control panel so the addon
       stops showing as "Installed".
    """
    site = getattr(setup_tool, "aq_parent", None)
    if site is not None:
        site._p_changed = True
    setup_tool.unsetLastVersionForProfile(PROFILE_ID)
    logger.info(
        "plone.registryfromenviron: v1 → v2 cleanup complete; "
        "profile unregistered from Add-ons panel"
    )
