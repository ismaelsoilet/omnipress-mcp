"""Runtime capability inspector and environment validator for OmniPress.

This module is a thin presentation layer over `src.core.capabilities`, the single
source of truth for external runtimes. It preserves the historical dictionary
shape for backward compatibility with the CLI and tests.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Any, Dict, Optional

from src.core.capabilities import capability_report, get_capabilities


def check_command_version(cmd: str, version_arg: str = "--version") -> Optional[str]:
    """Returns trimmed version string if command exists and succeeds, else None."""
    from pathlib import Path

    is_path = "/" in cmd or "\\" in cmd
    if not ((is_path and Path(cmd).is_file() and os.access(cmd, os.X_OK)) or shutil.which(cmd)):
        return None
    try:
        out = subprocess.check_output(
            [cmd, version_arg], stderr=subprocess.STDOUT, text=True, timeout=3
        )
        return out.strip().split("\n")[0]
    except Exception:
        return "installed (version unknown)"


def get_runtime_capabilities() -> Dict[str, Any]:
    """Returns the legacy capability dictionary plus the full registry snapshot."""
    snapshot = get_capabilities()

    def entry(name: str) -> Dict[str, Any]:
        info = snapshot[name]
        return {"available": info.available, "version": info.version}

    node = entry("node")
    ffmpeg = entry("ffmpeg")
    edge_tts = entry("edge_tts")
    blender = entry("blender")

    return {
        "python": entry("python"),
        "node": node,
        "npm": entry("npm"),
        "ffmpeg": ffmpeg,
        "edge_tts": edge_tts,
        "blender": blender,
        "whisper": entry("whisper"),
        "ai_image": entry("ai_image"),
        "ai_music": entry("ai_music"),
        "remotion_ready": snapshot["remotion"].available,
        "video_capable": bool(node["available"] and ffmpeg["available"]),
        "audio_capable": bool(edge_tts["available"] and ffmpeg["available"]),
        "blender_3d_capable": bool(blender["available"]),
        "capabilities": {name: info.to_dict() for name, info in snapshot.items()},
    }


def format_doctor_report(caps: Optional[Dict[str, Any]] = None) -> str:
    """Formats an executive health check report for CLI and diagnostics."""
    if caps is None:
        caps = get_runtime_capabilities()

    lines = [
        "============================================================",
        "          OmniPress MCP — Environment Diagnostic            ",
        "============================================================",
    ]

    py_v = caps["python"]["version"]
    lines.append(f"  Python Runtime : [OK] {py_v}")

    node_ok = caps["node"]["available"]
    node_v = caps["node"]["version"]
    lines.append(f"  Node.js (Video): [{'OK' if node_ok else 'MISSING'}] {node_v}")

    ff_ok = caps["ffmpeg"]["available"]
    ff_v = caps["ffmpeg"]["version"]
    lines.append(f"  FFmpeg Engine  : [{'OK' if ff_ok else 'MISSING'}] {ff_v}")

    tts_ok = caps["edge_tts"]["available"]
    lines.append(f"  Edge-TTS Audio : [{'OK' if tts_ok else 'MISSING'}] {caps['edge_tts']['version']}")

    blender_ok = caps.get("blender", {}).get("available", False)
    blender_v = caps.get("blender", {}).get("version", "Not found")
    lines.append(f"  Blender 3D     : [{'OK' if blender_ok else 'OPTIONAL'}] {blender_v}")

    remotion_ok = bool(caps.get("remotion_ready", False))
    lines.append(f"  Remotion CLI   : [{'OK' if remotion_ok else 'OPTIONAL'}] {'ready' if remotion_ok else 'Not found'}")

    whisper_ok = caps.get("whisper", {}).get("available", False)
    lines.append(f"  Whisper STT    : [{'OK' if whisper_ok else 'OPTIONAL'}] {caps.get('whisper', {}).get('version', 'Not found')}")

    ai_image_ok = caps.get("ai_image", {}).get("available", False)
    lines.append(f"  AI Image Gen   : [{'OK' if ai_image_ok else 'OPTIONAL'}] {caps.get('ai_image', {}).get('version', 'Not found')}")

    lines.append("------------------------------------------------------------")
    lines.append("Capabilities Summary:")
    lines.append(f"  - Long-Form Articles & Markdown : [READY] (Native Python)")
    lines.append(f"  - 3:4 Social Carousels (Pillow) : [READY] (Native Python)")
    lines.append(f"  - Neural Voiceover Generation   : [{'READY' if caps['audio_capable'] else 'DEGRADED (Requires edge-tts + ffmpeg)'}]")
    lines.append(f"  - Programmatic Video (Remotion) : [{'READY' if caps['video_capable'] else 'DEGRADED (Requires Node.js 20+ and ffmpeg)'}]")
    lines.append(f"  - 3D Assets & Mockups (Blender) : [{'READY' if caps.get('blender_3d_capable') else 'OPTIONAL (Requires Blender 4.2+ LTS)'}]")

    registry = caps.get("capabilities") or {}
    if registry:
        lines.append("------------------------------------------------------------")
        lines.append("Capability Registry (source of truth):")
        for name in sorted(registry):
            info = registry[name]
            status = "OK" if info.get("available") else ("PLANNED" if info.get("planned") else "MISSING")
            binary = info.get("binary") or "-"
            env_var = info.get("env_var") or "-"
            consumers = ", ".join(info.get("consumers") or []) or "-"
            lines.append(
                f"  {name:<12} [{status:<7}] bin={binary} env={env_var} consumers={consumers}"
            )
            if not info.get("available") and not info.get("planned"):
                lines.append(f"               hint: {info.get('install_hint', '')}")
    lines.append("============================================================")

    return "\n".join(lines)


def format_doctor_json() -> Dict[str, Any]:
    """Machine-readable doctor report for CI and agents."""
    return capability_report()
