"""Tests for plone.registryfromenviron."""

from plone.registry import field as reg_field
from plone.registry.registry import Registry
from unittest.mock import MagicMock

import pytest


# ── Fixtures ──────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _clean_overrides():
    """Reset module-level override dicts before/after each test."""
    from plone.registryfromenviron import environ

    orig_raw = environ.RAW_OVERRIDES.copy()
    orig_coerced = environ._COERCED.copy()
    environ.RAW_OVERRIDES.clear()
    environ._COERCED.clear()
    yield environ
    environ.RAW_OVERRIDES.clear()
    environ.RAW_OVERRIDES.update(orig_raw)
    environ._COERCED.clear()
    environ._COERCED.update(orig_coerced)


@pytest.fixture
def registry():
    """A plain plone.registry Registry with test records for each field type."""
    reg = Registry()
    reg._records._fields["my.textline"] = reg_field.TextLine(title="A text")
    reg._records._values["my.textline"] = "original"
    reg._records._fields["my.text"] = reg_field.Text(title="A text block")
    reg._records._values["my.text"] = "original text"
    reg._records._fields["my.number"] = reg_field.Int(title="A number")
    reg._records._values["my.number"] = 0
    reg._records._fields["my.flag"] = reg_field.Bool(title="A flag")
    reg._records._values["my.flag"] = False
    reg._records._fields["my.rate"] = reg_field.Float(title="A rate")
    reg._records._values["my.rate"] = 0.0
    reg._records._fields["my.items"] = reg_field.List(
        title="Items",
        value_type=reg_field.TextLine(),
    )
    reg._records._values["my.items"] = []
    reg._records._fields["my.pair"] = reg_field.Tuple(
        title="Pair",
        value_type=reg_field.TextLine(),
    )
    reg._records._values["my.pair"] = ()
    reg._records._fields["my.tags"] = reg_field.Set(
        title="Tags",
        value_type=reg_field.TextLine(),
    )
    reg._records._values["my.tags"] = set()
    reg._records._fields["my.frozen"] = reg_field.FrozenSet(
        title="Frozen",
        value_type=reg_field.TextLine(),
    )
    reg._records._values["my.frozen"] = frozenset()
    reg._records._fields["my.mapping"] = reg_field.Dict(
        title="Mapping",
        key_type=reg_field.TextLine(),
        value_type=reg_field.TextLine(),
    )
    reg._records._values["my.mapping"] = {}
    return reg


# ── coerce_value tests ───────────────────────────────────────────


class TestCoerceValue:
    """Test coerce_value for every supported field type."""

    def test_bool_true_variants(self):
        from plone.registryfromenviron.environ import coerce_value

        f = reg_field.Bool()
        for val in ("true", "True", "TRUE", "1", "yes", "on"):
            assert coerce_value(val, f) is True

    def test_bool_false_variants(self):
        from plone.registryfromenviron.environ import coerce_value

        f = reg_field.Bool()
        for val in ("false", "False", "0", "no", "off", ""):
            assert coerce_value(val, f) is False

    def test_int(self):
        from plone.registryfromenviron.environ import coerce_value

        assert coerce_value("42", reg_field.Int()) == 42
        assert coerce_value("-7", reg_field.Int()) == -7

    def test_int_invalid(self):
        from plone.registryfromenviron.environ import coerce_value

        with pytest.raises(ValueError):
            coerce_value("not_a_number", reg_field.Int())

    def test_float(self):
        from plone.registryfromenviron.environ import coerce_value

        assert coerce_value("3.14", reg_field.Float()) == 3.14

    def test_float_invalid(self):
        from plone.registryfromenviron.environ import coerce_value

        with pytest.raises(ValueError):
            coerce_value("not_a_float", reg_field.Float())

    def test_decimal(self):
        from decimal import Decimal
        from plone.registryfromenviron.environ import coerce_value

        result = coerce_value("1.23", reg_field.Decimal())
        assert result == Decimal("1.23")

    def test_list(self):
        from plone.registryfromenviron.environ import coerce_value

        f = reg_field.List(value_type=reg_field.TextLine())
        assert coerce_value('["a", "b"]', f) == ["a", "b"]

    def test_tuple(self):
        from plone.registryfromenviron.environ import coerce_value

        f = reg_field.Tuple(value_type=reg_field.TextLine())
        assert coerce_value('["a", "b"]', f) == ("a", "b")

    def test_set(self):
        from plone.registryfromenviron.environ import coerce_value

        f = reg_field.Set(value_type=reg_field.TextLine())
        assert coerce_value('["a", "b"]', f) == {"a", "b"}

    def test_frozenset(self):
        from plone.registryfromenviron.environ import coerce_value

        f = reg_field.FrozenSet(value_type=reg_field.TextLine())
        assert coerce_value('["a", "b"]', f) == frozenset({"a", "b"})

    def test_dict(self):
        from plone.registryfromenviron.environ import coerce_value

        f = reg_field.Dict(
            key_type=reg_field.TextLine(),
            value_type=reg_field.TextLine(),
        )
        assert coerce_value('{"k": "v"}', f) == {"k": "v"}

    def test_json_invalid(self):
        from json import JSONDecodeError
        from plone.registryfromenviron.environ import coerce_value

        f = reg_field.List(value_type=reg_field.TextLine())
        with pytest.raises(JSONDecodeError):
            coerce_value("not json", f)

    def test_textline_passthrough(self):
        from plone.registryfromenviron.environ import coerce_value

        assert coerce_value("hello", reg_field.TextLine()) == "hello"

    def test_text_passthrough(self):
        from plone.registryfromenviron.environ import coerce_value

        assert coerce_value("multi\nline", reg_field.Text()) == "multi\nline"

    def test_ascii_passthrough(self):
        from plone.registryfromenviron.environ import coerce_value

        assert coerce_value("ascii", reg_field.ASCII()) == "ascii"


# ── get_override tests ───────────────────────────────────────────


class TestGetOverride:
    def test_no_override_returns_marker(self, _clean_overrides, registry):
        from plone.registryfromenviron.environ import _MARKER
        from plone.registryfromenviron.environ import get_override

        assert get_override(registry, "my.textline") is _MARKER

    def test_override_hit(self, _clean_overrides, registry):
        from plone.registryfromenviron.environ import get_override

        _clean_overrides.RAW_OVERRIDES["my.textline"] = "overridden"
        assert get_override(registry, "my.textline") == "overridden"

    def test_override_cached_on_second_call(self, _clean_overrides, registry):
        from plone.registryfromenviron.environ import _COERCED
        from plone.registryfromenviron.environ import get_override

        _clean_overrides.RAW_OVERRIDES["my.number"] = "99"
        assert get_override(registry, "my.number") == 99
        assert "my.number" in _COERCED
        # second call hits cache
        assert get_override(registry, "my.number") == 99

    def test_unknown_key_returns_marker(self, _clean_overrides, registry):
        from plone.registryfromenviron.environ import _MARKER
        from plone.registryfromenviron.environ import get_override

        _clean_overrides.RAW_OVERRIDES["no.such.key"] = "value"
        assert get_override(registry, "no.such.key") is _MARKER

    def test_invalid_value_returns_marker(self, _clean_overrides, registry):
        from plone.registryfromenviron.environ import _MARKER
        from plone.registryfromenviron.environ import get_override

        _clean_overrides.RAW_OVERRIDES["my.number"] = "not_a_number"
        assert get_override(registry, "my.number") is _MARKER

    def test_fieldref_resolved(self, _clean_overrides, registry):
        """FieldRef records should resolve to the original field for coercion."""
        from plone.registryfromenviron.environ import get_override

        # Create a field ref: my.alias -> my.number
        registry._records._fields["my.alias"] = "my.number"
        registry._records._values["my.alias"] = 0
        _clean_overrides.RAW_OVERRIDES["my.alias"] = "77"
        assert get_override(registry, "my.alias") == 77


# ── EnvOverrideRegistry tests ────────────────────────────────────


class TestEnvOverrideRegistry:
    def test_getitem_with_override(self, _clean_overrides, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        registry.__class__ = EnvOverrideRegistry
        _clean_overrides.RAW_OVERRIDES["my.textline"] = "from_env"
        assert registry["my.textline"] == "from_env"

    def test_getitem_fallback_to_zodb(self, _clean_overrides, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        registry.__class__ = EnvOverrideRegistry
        assert registry["my.textline"] == "original"

    def test_getitem_keyerror_for_missing(self, _clean_overrides, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        registry.__class__ = EnvOverrideRegistry
        with pytest.raises(KeyError):
            registry["no.such.key"]

    def test_get_with_override(self, _clean_overrides, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        registry.__class__ = EnvOverrideRegistry
        _clean_overrides.RAW_OVERRIDES["my.number"] = "42"
        assert registry.get("my.number") == 42

    def test_get_fallback_to_zodb(self, _clean_overrides, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        registry.__class__ = EnvOverrideRegistry
        assert registry.get("my.textline") == "original"

    def test_get_returns_default_for_missing(self, _clean_overrides, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        registry.__class__ = EnvOverrideRegistry
        assert registry.get("no.such.key", "default") == "default"

    def test_get_returns_none_for_missing_no_default(self, _clean_overrides, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        registry.__class__ = EnvOverrideRegistry
        assert registry.get("no.such.key") is None

    def test_bool_override(self, _clean_overrides, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        registry.__class__ = EnvOverrideRegistry
        _clean_overrides.RAW_OVERRIDES["my.flag"] = "true"
        assert registry["my.flag"] is True

    def test_list_override(self, _clean_overrides, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        registry.__class__ = EnvOverrideRegistry
        _clean_overrides.RAW_OVERRIDES["my.items"] = '["x", "y"]'
        assert registry["my.items"] == ["x", "y"]

    def test_float_override(self, _clean_overrides, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        registry.__class__ = EnvOverrideRegistry
        _clean_overrides.RAW_OVERRIDES["my.rate"] = "9.81"
        assert registry["my.rate"] == 9.81

    def test_dict_override(self, _clean_overrides, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        registry.__class__ = EnvOverrideRegistry
        _clean_overrides.RAW_OVERRIDES["my.mapping"] = '{"a": "1"}'
        assert registry["my.mapping"] == {"a": "1"}

    def test_is_subclass_of_base(self):
        from plone.app.registry.registry import Registry as BaseAppRegistry
        from plone.registryfromenviron.registry import EnvOverrideRegistry

        assert issubclass(EnvOverrideRegistry, BaseAppRegistry)


# ── setuphandlers tests ──────────────────────────────────────────


class TestSetupHandlers:
    def _make_context(self, marker_file, site):
        ctx = MagicMock()
        ctx.readDataFile.side_effect = lambda f: "marker" if f == marker_file else None
        ctx.getSite.return_value = site
        return ctx

    def test_install_swaps_class(self, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry
        from plone.registryfromenviron.setuphandlers import install

        site = MagicMock()
        site.portal_registry = registry
        ctx = self._make_context("install_marker.txt", site)
        install(ctx)
        assert isinstance(registry, EnvOverrideRegistry)

    def test_install_already_swapped_is_noop(self, registry):
        from plone.registryfromenviron.registry import EnvOverrideRegistry
        from plone.registryfromenviron.setuphandlers import install

        registry.__class__ = EnvOverrideRegistry
        site = MagicMock()
        site.portal_registry = registry
        ctx = self._make_context("install_marker.txt", site)
        install(ctx)
        assert isinstance(registry, EnvOverrideRegistry)

    def test_install_no_marker_skips(self):
        from plone.registryfromenviron.setuphandlers import install

        ctx = MagicMock()
        ctx.readDataFile.return_value = None
        install(ctx)
        ctx.getSite.assert_not_called()

    def test_install_no_registry_is_safe(self):
        from plone.registryfromenviron.setuphandlers import install

        site = MagicMock(spec=[])
        ctx = self._make_context("install_marker.txt", site)
        install(ctx)

    def test_uninstall_reverts_class(self, registry):
        from plone.app.registry.registry import Registry as BaseAppRegistry
        from plone.registryfromenviron.registry import EnvOverrideRegistry
        from plone.registryfromenviron.setuphandlers import uninstall

        registry.__class__ = EnvOverrideRegistry
        site = MagicMock()
        site.portal_registry = registry
        ctx = self._make_context("uninstall_marker.txt", site)
        uninstall(ctx)
        assert type(registry) is BaseAppRegistry

    def test_uninstall_not_swapped_is_noop(self, registry):
        from plone.registryfromenviron.setuphandlers import uninstall

        site = MagicMock()
        site.portal_registry = registry
        ctx = self._make_context("uninstall_marker.txt", site)
        uninstall(ctx)

    def test_uninstall_no_marker_skips(self):
        from plone.registryfromenviron.setuphandlers import uninstall

        ctx = MagicMock()
        ctx.readDataFile.return_value = None
        uninstall(ctx)
        ctx.getSite.assert_not_called()

    def test_uninstall_no_registry_is_safe(self):
        from plone.registryfromenviron.setuphandlers import uninstall

        site = MagicMock(spec=[])
        ctx = self._make_context("uninstall_marker.txt", site)
        uninstall(ctx)


# ── env var scanning tests ───────────────────────────────────────


class TestEnvVarScanning:
    """Test the module-level env var scanning logic."""

    def test_double_underscore_to_dot(self):
        from plone.registryfromenviron.environ import PREFIX

        key = "PLONE_REGISTRY_plone__smtp_host"
        assert key[len(PREFIX) :].replace("__", ".") == "plone.smtp_host"

    def test_single_underscore_preserved(self):
        from plone.registryfromenviron.environ import PREFIX

        key = "PLONE_REGISTRY_my__app__some_setting"
        assert key[len(PREFIX) :].replace("__", ".") == "my.app.some_setting"

    def test_scanning_with_env_vars(self, monkeypatch):
        """Verify that scan_environ picks up PLONE_REGISTRY_* vars."""
        monkeypatch.setenv("PLONE_REGISTRY_plone__smtp_host", "mail.test.com")
        monkeypatch.setenv("PLONE_REGISTRY_plone__flag", "true")
        monkeypatch.setenv("UNRELATED_VAR", "ignore")

        from plone.registryfromenviron.environ import scan_environ

        result = scan_environ()
        assert result == {
            "plone.smtp_host": "mail.test.com",
            "plone.flag": "true",
        }
