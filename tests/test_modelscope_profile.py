"""ModelScope provider profile wiring.

Asserts the bundled ``plugins/model-providers/modelscope/`` profile registers
with the expected OpenAI-compatible endpoint, API-key env var, and offline
catalog. Registration itself is covered generically by the provider discovery
mechanism in Hermes; this test pins the ModelScope-specific values so a typo
in the endpoint or env var fails CI rather than silently routing to the wrong
place.

These tests use stubbed Hermes provider APIs so they run even when Hermes is
not installed in the test environment.
"""

from __future__ import annotations

import importlib
import sys
import types
from typing import Any
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Stub the ``providers`` package so the plugin module can be imported and its
# ``register_provider()`` call captured, without requiring a full Hermes
# installation.
# ---------------------------------------------------------------------------

@pytest.fixture
def stub_providers(monkeypatch):
    """Inject a fake ``providers`` package into sys.modules."""
    pkg = types.ModuleType("providers")
    pkg._REGISTRY: dict[str, Any] = {}
    pkg._ALIASES: dict[str, str] = {}
    pkg._discovered = False

    base = types.ModuleType("providers.base")

    class ProviderProfile:
        def __init__(self, **kwargs: Any) -> None:
            self.__dict__.update(kwargs)
            # Derive api_mode from defaults that Hermes would set
            self.api_mode = kwargs.get("api_mode", "chat_completions")

    base.ProviderProfile = ProviderProfile
    pkg.base = base

    def register_provider(profile: Any) -> None:
        pkg._REGISTRY[profile.name] = profile
        for alias in getattr(profile, "aliases", ()):
            pkg._ALIASES[alias] = profile.name

    pkg.register_provider = register_provider

    def list_providers() -> list[Any]:
        return list(pkg._REGISTRY.values())

    def get_provider_profile(name: str) -> Any | None:
        resolved = pkg._ALIASES.get(name, name)
        return pkg._REGISTRY.get(resolved)

    pkg.list_providers = list_providers
    pkg.get_provider_profile = get_provider_profile

    monkeypatch.setitem(sys.modules, "providers", pkg)
    monkeypatch.setitem(sys.modules, "providers.base", base)

    # Now import the plugin module so register_provider() fires.
    mod_path = (
        __import__("pathlib").Path(__file__)
        .resolve()
        .parent.parent
        / "plugins" / "model-providers" / "modelscope" / "__init__.py"
    )
    spec = importlib.util.spec_from_file_location("modelscope_plugin", mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    return pkg


# ---------------------------------------------------------------------------
# Profile shape
# ---------------------------------------------------------------------------

class TestModelScopeProfile:
    def test_profile_registered(self, stub_providers):
        p = stub_providers.get_provider_profile("modelscope")
        assert p is not None, "modelscope profile not discovered"

    def test_name(self, stub_providers):
        p = stub_providers.get_provider_profile("modelscope")
        assert p.name == "modelscope"

    def test_base_url(self, stub_providers):
        p = stub_providers.get_provider_profile("modelscope")
        assert p.base_url == "https://api-inference.modelscope.cn/v1"

    def test_api_mode(self, stub_providers):
        p = stub_providers.get_provider_profile("modelscope")
        assert p.api_mode == "chat_completions"

    def test_auth_type(self, stub_providers):
        p = stub_providers.get_provider_profile("modelscope")
        assert p.auth_type == "api_key"

    def test_env_vars_include_api_key(self, stub_providers):
        p = stub_providers.get_provider_profile("modelscope")
        assert "MODELSCOPE_API_KEY" in p.env_vars

    def test_env_vars_include_base_url_override(self, stub_providers):
        p = stub_providers.get_provider_profile("modelscope")
        assert "MODELSCOPE_BASE_URL" in p.env_vars

    def test_display_name(self, stub_providers):
        p = stub_providers.get_provider_profile("modelscope")
        assert p.display_name == "ModelScope"

    def test_signup_url(self, stub_providers):
        p = stub_providers.get_provider_profile("modelscope")
        assert p.signup_url == "https://modelscope.cn"


# ---------------------------------------------------------------------------
# Aliases
# ---------------------------------------------------------------------------

class TestModelScopeAliases:
    def test_ms_alias(self, stub_providers):
        p = stub_providers.get_provider_profile("ms")
        assert p is not None
        assert p.name == "modelscope"


# ---------------------------------------------------------------------------
# Fallback catalog
# ---------------------------------------------------------------------------

class TestModelScopeFallbackModels:
    def test_catalog_not_empty(self, stub_providers):
        p = stub_providers.get_provider_profile("modelscope")
        assert len(p.fallback_models) >= 1

    def test_org_name_format(self, stub_providers):
        """ModelScope model IDs use org/name format (e.g. Qwen/Qwen3.5-27B)."""
        p = stub_providers.get_provider_profile("modelscope")
        for model in p.fallback_models:
            assert "/" in model, f"model {model!r} missing org/ prefix"

    def test_default_aux_model_in_catalog(self, stub_providers):
        p = stub_providers.get_provider_profile("modelscope")
        assert p.default_aux_model in p.fallback_models


# ---------------------------------------------------------------------------
# Manifest (plugin.yaml)
# ---------------------------------------------------------------------------

class TestModelScopeManifest:
    def test_manifest_exists(self):
        import pathlib
        manifest = (
            pathlib.Path(__file__).resolve().parent.parent
            / "plugins" / "model-providers" / "modelscope" / "plugin.yaml"
        )
        assert manifest.exists(), "plugin.yaml not found"

    def test_manifest_kind(self):
        import pathlib
        import yaml
        manifest = (
            pathlib.Path(__file__).resolve().parent.parent
            / "plugins" / "model-providers" / "modelscope" / "plugin.yaml"
        )
        data = yaml.safe_load(manifest.read_text())
        assert data["kind"] == "model-provider"

    def test_manifest_name(self):
        import pathlib
        import yaml
        manifest = (
            pathlib.Path(__file__).resolve().parent.parent
            / "plugins" / "model-providers" / "modelscope" / "plugin.yaml"
        )
        data = yaml.safe_load(manifest.read_text())
        assert data["name"] == "modelscope-provider"