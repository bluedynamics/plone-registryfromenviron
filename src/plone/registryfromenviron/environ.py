"""Scan os.environ for PLONE_REGISTRY_* variables and coerce to field types."""

import json
import logging
import os

from plone.registry.fieldref import FieldRef
from zope.schema import interfaces as schema_ifaces


logger = logging.getLogger(__name__)

PREFIX = "PLONE_REGISTRY_"
_MARKER = object()


def scan_environ():
    """Scan os.environ for PLONE_REGISTRY_* variables.

    Returns a dict mapping registry keys (dots) to raw string values.
    Double underscores in env var names are converted to dots.
    """
    return {
        key[len(PREFIX):].replace("__", "."): value
        for key, value in os.environ.items()
        if key.startswith(PREFIX)
    }


# Scanned once at import time — env vars don't change at runtime.
RAW_OVERRIDES: dict[str, str] = scan_environ()

if RAW_OVERRIDES:
    logger.info(
        "Registry overrides from environment: %s",
        ", ".join(sorted(RAW_OVERRIDES)),
    )

# Lazy coercion cache — filled on first access per key, lives for process lifetime.
_COERCED: dict[str, object] = {}


def get_override(registry, name):
    """Return coerced override value, or _MARKER if no override."""
    if name not in RAW_OVERRIDES:
        return _MARKER
    if name not in _COERCED:
        try:
            field = registry.records._getField(name)
            if isinstance(field, FieldRef):
                field = field.originalField
            _COERCED[name] = coerce_value(RAW_OVERRIDES[name], field)
        except KeyError:
            logger.warning("Env override for unknown registry key: %s", name)
            return _MARKER
        except (ValueError, TypeError, json.JSONDecodeError):
            logger.exception("Invalid env override value for key: %s", name)
            return _MARKER
    return _COERCED[name]


def coerce_value(raw, field):
    """Convert env var string to the field's expected Python type."""
    if schema_ifaces.IBool.providedBy(field):
        return raw.lower() in ("true", "1", "yes", "on")
    if schema_ifaces.IInt.providedBy(field):
        return int(raw)
    if schema_ifaces.IFloat.providedBy(field):
        return float(raw)
    if schema_ifaces.IDecimal.providedBy(field):
        from decimal import Decimal

        return Decimal(raw)
    if schema_ifaces.ITuple.providedBy(field):
        return tuple(json.loads(raw))
    if schema_ifaces.IList.providedBy(field):
        return list(json.loads(raw))
    if schema_ifaces.ISet.providedBy(field):
        return set(json.loads(raw))
    if schema_ifaces.IFrozenSet.providedBy(field):
        return frozenset(json.loads(raw))
    if schema_ifaces.IDict.providedBy(field):
        return json.loads(raw)
    # TextLine, Text, ASCII, BytesLine, URI, Choice, etc.
    return raw
