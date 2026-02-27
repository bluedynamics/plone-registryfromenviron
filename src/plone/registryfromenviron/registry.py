"""EnvOverrideRegistry — Registry subclass checking env vars before ZODB."""

from .environ import _MARKER
from .environ import get_override
from plone.app.registry.registry import Registry as BaseAppRegistry


class EnvOverrideRegistry(BaseAppRegistry):
    """Registry that checks environment variables before ZODB values."""

    def __getitem__(self, name):
        value = get_override(self, name)
        if value is not _MARKER:
            return value
        return super().__getitem__(name)

    def get(self, name, default=None):
        value = get_override(self, name)
        if value is not _MARKER:
            return value
        return super().get(name, default)
