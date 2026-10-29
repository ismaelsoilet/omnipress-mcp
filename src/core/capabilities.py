"""Central capability registry for OmniPress.

Single source of truth for external runtimes and optional services.
Every probe runs at call time (never in a constructor) so a binary installed,
removed or relocated after import is reflected immediately.

Consumers:
- `omnipress doctor` (human-readable + --json)
- every engine/provider before invoking an external runtime
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class CapabilityInfo:
    name: str
    available: bool
    version: str
    binary: str
    required: bool
    consumers: Tuple[str, ...]
    install_hint: str
    env_var: Optional[str] = None
    planned: bool = False
    extra: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "available": self.available,
            "version": self.version,
            "binary": self.binary,
            "required": self.required,
            "consumers": list(self.consumers),
            "install_hint": self.install_hint,
            "env_var": self.env_var,
            "planned": self.planned,
            "extra": dict(self.extra),
        }


def _command_version(cmd: str, version_arg: str = "--version") -> Optional[str]:
    if not cmd:
        return None
    is_path = "/" in cmd or "\\" in cmd
    if not ((is_path and Path(cmd).is_file() and os.access(cmd, os.X_OK)) or shutil.which(cmd)):
        return None
    try:
        out = subprocess.check_output(
            [cmd, version_arg], stderr=subprocess.STDOUT, text=True, timeout=4
        )
        first = out.strip().split("\n")[0].strip()
        return first or "installed"
    except Exception:
        return "installed (version unknown)"


def _which(*names: str) -> Optional[str]:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def resolve_blender_binary(channel_slug: Optional[str] = None) -> Optional[str]:
    env_path = ""
    if channel_slug:
        try:
            from src.core.channel_manager import ChannelManager

            env_path = ChannelManager().get_credential("BLENDER_PATH", channel_slug)
        except Exception:
            env_path = ""
    env_path = env_path or os.getenv("BLENDER_PATH", "").strip()
    if env_path and Path(env_path).is_file() and os.access(env_path, os.X_OK):
        return env_path

    which_bin = shutil.which("blender")
    if which_bin:
        return which_bin

    for candidate in (
        Path.home() / ".local" / "bin" / "blender",
        Path("/usr/local/bin/blender"),
        Path("/usr/bin/blender"),
        Path("/snap/bin/blender"),
    ):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def resolve_ffmpeg_binary(channel_slug: Optional[str] = None) -> Optional[str]:
    env_path = ""
    if channel_slug:
        try:
            from src.core.channel_manager import ChannelManager

            env_path = ChannelManager().get_credential("FFMPEG_PATH", channel_slug)
        except Exception:
            env_path = ""
    env_path = env_path or os.getenv("FFMPEG_PATH", "").strip()
    if env_path and Path(env_path).is_file() and os.access(env_path, os.X_OK):
        return env_path
    local = PROJECT_ROOT / "bin" / "ffmpeg"
    if local.is_file() and os.access(local, os.X_OK):
        return str(local)
    return shutil.which("ffmpeg")


def _probe_ffmpeg() -> Tuple[bool, str, str]:
    binary = resolve_ffmpeg_binary() or "ffmpeg"
    version = _command_version(binary, "-version")
    if version and version.startswith("ffmpeg version"):
        parts = version.split()
        version = parts[2] if len(parts) > 2 else version
    return bool(version and version != "Not found"), version or "Not found", binary


def _probe_edge_tts() -> Tuple[bool, str, str]:
    try:
        import edge_tts  # noqa: F401

        return True, getattr(edge_tts, "__version__", "installed"), "python-module"
    except ImportError:
        return False, "Not found", "python-module"


def _probe_remotion() -> Tuple[bool, str, str]:
    node = shutil.which("node")
    if not node:
        return False, "Not found", "node"
    package = PROJECT_ROOT / "node_modules" / "@remotion" / "cli"
    npx = shutil.which("npx") or shutil.which("remotion")
    available = bool(npx and package.exists())
    return available, "installed" if available else "Not found", npx or "npx"


def _probe_whisper() -> Tuple[bool, str, str]:
    binary = _which("whisper", "faster-whisper", "whisper-ctranslate2")
    if binary:
        return True, _command_version(binary, "--help") or "installed", binary
    try:
        import faster_whisper  # noqa: F401

        return True, "python-module", "python-module"
    except ImportError:
        return False, "Not found", "Not found"


def _probe_ai_image() -> Tuple[bool, str, str]:
    keys = {
        "GEMINI_API_KEY": "gemini",
        "GOOGLE_API_KEY": "gemini",
        "OPENAI_API_KEY": "openai",
        "REPLICATE_API_TOKEN": "replicate",
        "FAL_KEY": "fal",
    }
    for env_var, provider in keys.items():
        if os.getenv(env_var, "").strip():
            return True, f"configured ({provider})", env_var
    return False, "Not configured", "GEMINI_API_KEY|OPENAI_API_KEY|REPLICATE_API_TOKEN|FAL_KEY"


def _probe_ai_music() -> Tuple[bool, str, str]:
    if os.getenv("GOOGLE_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip():
        return True, "configured (lyria)", "GOOGLE_API_KEY"
    return False, "Not configured", "GOOGLE_API_KEY"


def _probe_network() -> Tuple[bool, str, str]:
    try:
        import requests  # noqa: F401

        return True, "requests available", "python-module"
    except ImportError:
        return False, "Not found", "python-module"


_DEFINITIONS: Dict[str, Dict[str, object]] = {
    "python": {
        "probe": lambda: (True, sys.version.split()[0], sys.executable),
        "required": True,
        "consumers": ("all",),
        "install_hint": "Install Python 3.10+.",
        "env_var": None,
    },
    "node": {
        "probe": lambda: (
            bool(shutil.which("node")),
            _command_version("node", "-v") or "Not found",
            shutil.which("node") or "node",
        ),
        "required": False,
        "consumers": ("remotion",),
        "install_hint": "Install Node.js 20+ (required by Remotion).",
        "env_var": None,
    },
    "npm": {
        "probe": lambda: (
            bool(shutil.which("npm")),
            _command_version("npm", "-v") or "Not found",
            shutil.which("npm") or "npm",
        ),
        "required": False,
        "consumers": ("remotion",),
        "install_hint": "Install npm (bundled with Node.js).",
        "env_var": None,
    },
    "ffmpeg": {
        "probe": _probe_ffmpeg,
        "required": True,
        "consumers": ("universal_audio", "universal_video", "documentary", "shorts"),
        "install_hint": "Install FFmpeg 6+ and/or set FFMPEG_PATH.",
        "env_var": "FFMPEG_PATH",
    },
    "edge_tts": {
        "probe": _probe_edge_tts,
        "required": False,
        "consumers": ("voice", "narration"),
        "install_hint": "Install with `pip install edge-tts`.",
        "env_var": None,
    },
    "remotion": {
        "probe": _probe_remotion,
        "required": False,
        "consumers": ("universal_video", "intro", "documentary"),
        "install_hint": "Run `npm install` (Node.js 20+ and @remotion/cli required).",
        "env_var": None,
    },
    "blender": {
        "probe": lambda: (
            bool(resolve_blender_binary()),
            _command_version(resolve_blender_binary() or "", "--version") or "Not found",
            resolve_blender_binary() or "blender",
        ),
        "required": False,
        "consumers": ("universal_3d", "thumbnail", "mockups"),
        "install_hint": "Install Blender 4.2+ LTS and/or set BLENDER_PATH.",
        "env_var": "BLENDER_PATH",
    },
    "whisper": {
        "probe": _probe_whisper,
        "required": False,
        "consumers": ("universal_captions", "universal_audio"),
        "install_hint": "Install `openai-whisper` or `faster-whisper`, or provide Whisper JSON externally.",
        "env_var": None,
    },
    "ai_image": {
        "probe": _probe_ai_image,
        "required": False,
        "consumers": ("image_recipe",),
        "install_hint": "Set GEMINI_API_KEY, OPENAI_API_KEY, REPLICATE_API_TOKEN or FAL_KEY.",
        "env_var": "GEMINI_API_KEY",
    },
    "ai_music": {
        "probe": _probe_ai_music,
        "required": False,
        "consumers": ("music_recipe",),
        "install_hint": "Set GOOGLE_API_KEY for Lyria (planned provider).",
        "env_var": "GOOGLE_API_KEY",
        "planned": True,
    },
    "network": {
        "probe": _probe_network,
        "required": False,
        "consumers": ("stock_asset", "ai_image", "publishing"),
        "install_hint": "Install `requests`.",
        "env_var": None,
    },
}


def get_capabilities() -> Dict[str, CapabilityInfo]:
    """Probes every capability now and returns an immutable snapshot."""
    snapshot: Dict[str, CapabilityInfo] = {}
    for name, spec in _DEFINITIONS.items():
        probe: Callable[[], Tuple[bool, str, str]] = spec["probe"]  # type: ignore[assignment]
        try:
            available, version, binary = probe()
        except Exception as exc:  # pragma: no cover - defensive
            available, version, binary = False, f"probe error: {exc}", "Not found"
        snapshot[name] = CapabilityInfo(
            name=name,
            available=available,
            version=version,
            binary=binary,
            required=bool(spec["required"]),
            consumers=tuple(spec["consumers"]),  # type: ignore[arg-type]
            install_hint=str(spec["install_hint"]),
            env_var=spec.get("env_var"),  # type: ignore[arg-type]
            planned=bool(spec.get("planned", False)),
        )
    return snapshot


def require_capability(name: str, channel_slug: Optional[str] = None) -> CapabilityInfo:
    """Returns the capability or raises an actionable error."""
    caps = get_capabilities()
    if name not in caps:
        raise KeyError(f"Unknown capability '{name}'. Known: {sorted(caps)}")
    info = caps[name]

    available = info.available
    if name == "blender" and not available and channel_slug:
        binary = resolve_blender_binary(channel_slug)
        if binary:
            available = True
            info = CapabilityInfo(
                name=info.name,
                available=True,
                version=info.version,
                binary=binary,
                required=info.required,
                consumers=info.consumers,
                install_hint=info.install_hint,
                env_var=info.env_var,
                planned=info.planned,
                extra=info.extra,
            )

    if not available:
        raise CapabilityUnavailable(name, info)
    return info


class CapabilityUnavailable(RuntimeError):
    """Raised when an engine needs a capability that is not installed."""

    def __init__(self, name: str, info: CapabilityInfo):
        self.name = name
        self.info = info
        hint = info.install_hint
        env = f" (env: {info.env_var})" if info.env_var else ""
        super().__init__(
            f"Capability '{name}' is not available.{env} {hint}\n"
            f"Run `omnipress doctor` for the full capability report."
        )


def capability_report() -> Dict[str, object]:
    """Serializable report consumed by `omnipress doctor --json`."""
    caps = get_capabilities()
    return {
        "capabilities": {name: info.to_dict() for name, info in caps.items()},
        "capabilities_summary": {
            "available": sorted(n for n, i in caps.items() if i.available),
            "missing": sorted(n for n, i in caps.items() if not i.available and not i.planned),
            "planned": sorted(n for n, i in caps.items() if i.planned),
        },
    }


def missing_required() -> List[CapabilityInfo]:
    return [i for i in get_capabilities().values() if i.required and not i.available]
