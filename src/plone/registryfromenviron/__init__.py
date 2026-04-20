"""plone.registryfromenviron — override registry values from environment variables.

Activation model: at first import, if any ``PLONE_REGISTRY_*`` env vars are set,
the package patches ``plone.registry.registry.Registry.__getitem__`` and ``.get``
to consult those variables before falling back to the ZODB-stored value.

If no matching env vars are present, the package is a no-op — no patching occurs
and there is zero runtime overhead.
"""

from .environ import RAW_OVERRIDES
from .patch import apply_patch


def _maybe_activate():
    """Apply the patch iff PLONE_REGISTRY_* env vars were found at startup."""
    if RAW_OVERRIDES:
        apply_patch()


_maybe_activate()
