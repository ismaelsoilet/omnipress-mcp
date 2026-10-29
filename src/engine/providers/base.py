"""Provider contract for every external runtime orchestrated by OmniPress.

A provider is the ONLY place where `src/` may spawn a subprocess or call an
external service. Engines receive a declarative spec, ask the provider to
validate it, then ask it to render/execute.

Rules enforced by tests:
- stateless: no mutable instance attributes outside __init__
- capability-gated: every execution calls `require_capability`
- path-safe: outputs never escape the resolved output directory
- fail-fast: `validate()` runs before any subprocess/network call
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, FrozenSet, Iterable, Optional, Type

from src.core.capabilities import CapabilityInfo, require_capability


class ProviderError(RuntimeError):
    """Base error for provider failures."""


class ProviderUnavailable(ProviderError):
    """Raised when the runtime behind a provider is not installed/configured."""


class Provider:
    """Base contract shared by render, media and source providers."""

    name: str = "base"
    capability: str = "python"
    supports: FrozenSet[str] = frozenset()

    def is_available(self) -> bool:
        try:
            require_capability(self.capability)
            return True
        except Exception:
            return False

    def info(self) -> Dict[str, Any]:
        info: CapabilityInfo = require_capability(self.capability)
        return {
            "provider": self.name,
            "capability": info.name,
            "available": info.available,
            "version": info.version,
            "binary": info.binary,
            "supports": sorted(self.supports),
        }

    def validate(self, spec: Dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if not isinstance(spec, dict):
            return ["spec must be an object"]
        return errors

    def _require(self, channel_slug: Optional[str] = None) -> CapabilityInfo:
        try:
            return require_capability(self.capability, channel_slug=channel_slug)
        except Exception as exc:
            raise ProviderUnavailable(str(exc)) from exc


class RenderProvider(Provider):
    """Provider that produces a file (image, video, audio, 3D asset)."""

    default_extension: str = "bin"

    @abstractmethod
    def render(self, spec: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
        """Produces the output file inside out_dir and returns a result manifest."""

    def resolve_output(
        self,
        out_dir: Path,
        output_name: Optional[str],
        default_stem: str = "render",
    ) -> Path:
        """Resolves a safe output path that cannot escape out_dir."""
        base = Path(out_dir).resolve()
        base.mkdir(parents=True, exist_ok=True)

        name = (output_name or f"{default_stem}.{self.default_extension}").strip()
        if not name:
            name = f"{default_stem}.{self.default_extension}"
        if Path(name).name != name:
            raise ProviderError(
                f"Unsafe output_name '{output_name}': path separators are not allowed."
            )

        candidate = (base / name).resolve()
        if not str(candidate).startswith(str(base) + os.sep) and candidate != base:
            raise ProviderError(f"Unsafe output path '{candidate}' escapes {base}.")
        candidate.parent.mkdir(parents=True, exist_ok=True)
        return candidate

    @staticmethod
    def ensure_within(base: Path, candidate: Path) -> Path:
        base_r = Path(base).resolve()
        cand_r = Path(candidate).resolve()
        if cand_r != base_r and not str(cand_r).startswith(str(base_r) + os.sep):
            raise ProviderError(f"Path '{cand_r}' escapes '{base_r}'.")
        return cand_r

    @staticmethod
    def check_required(spec: Dict[str, Any], keys: Iterable[str]) -> list[str]:
        return [f"missing required field '{k}'" for k in keys if spec.get(k) in (None, "")]


def file_sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Provider registry (kept here to avoid circular imports with the package)
# ---------------------------------------------------------------------------

_REGISTRY: Dict[str, Type[Provider]] = {}


def register(provider_cls: Type[Provider]) -> Type[Provider]:
    name = getattr(provider_cls, "name", "").strip()
    if not name:
        raise ProviderError(f"Provider {provider_cls!r} has no name.")
    _REGISTRY[name] = provider_cls
    return provider_cls


def _load_builtin_providers() -> None:
    if _REGISTRY:
        return
    from src.engine.providers import (  # noqa: F401
        ai_image_provider,
        blender_provider,
        edge_tts_provider,
        ffmpeg_provider,
        prompt_export_provider,
        remotion_provider,
        stock_asset_provider,
        whisper_provider,
    )


def get_provider(name: str) -> Provider:
    normalized = (name or "").strip().lower()
    if normalized not in _REGISTRY:
        _load_builtin_providers()
    if normalized not in _REGISTRY:
        raise ProviderError(f"Unknown provider '{name}'. Available: {sorted(_REGISTRY)}")
    return _REGISTRY[normalized]()


def available_providers() -> Dict[str, bool]:
    _load_builtin_providers()
    result: Dict[str, bool] = {}
    for name, cls in sorted(_REGISTRY.items()):
        try:
            result[name] = cls().is_available()
        except Exception:
            result[name] = False
    return result


def provider_for(spec: Dict[str, Any], default: Optional[str] = None) -> Provider:
    name = str(spec.get("provider") or default or "").strip()
    if not name:
        raise ProviderError("Spec does not declare a 'provider'.")
    return get_provider(name)
