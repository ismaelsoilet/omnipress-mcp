"""Runtime capability inspector and environment validator for OmniPress."""

import os
import shutil
import subprocess
import sys
from typing import Dict, Any, Optional


def check_command_version(cmd: str, version_arg: str = "--version") -> Optional[str]:
    """Returns trimmed version string if command exists and succeeds, else None."""
    from pathlib import Path
    is_path = "/" in cmd or "\\" in cmd
    if not (is_path and Path(cmd).is_file() and os.access(cmd, os.X_OK)) and not shutil.which(cmd):
        return None
    try:
        out = subprocess.check_output([cmd, version_arg], stderr=subprocess.STDOUT, text=True, timeout=3)
        return out.strip().split("\n")[0]
    except Exception:
        return "installed (version unknown)"


def get_runtime_capabilities() -> Dict[str, Any]:
    """
    Evaluates installed system runtimes and optional multimedia dependencies:
    - python: Current runtime version
    - node: Node.js 20+ required for Remotion video engine
    - npm: Node package manager
    - ffmpeg: Media converter required for audio stitching and video encoding
    - edge_tts: Neural text-to-speech engine
    - remotion_cli: Local Remotion CLI in node_modules or global
    """
    # Check edge-tts
    edge_tts_installed = False
    try:
        import edge_tts
        edge_tts_installed = True
    except ImportError:
        pass

    node_version = check_command_version("node", "-v")
    npm_version = check_command_version("npm", "-v")

    try:
        from src.engine.universal_audio import find_ffmpeg_binary
        ffmpeg_bin = find_ffmpeg_binary()
    except Exception:
        ffmpeg_bin = "ffmpeg"

    ffmpeg_version = check_command_version(ffmpeg_bin, "-version")
    if ffmpeg_version and "ffmpeg version" in ffmpeg_version:
        ffmpeg_version = ffmpeg_version.split()[2]

    # Check remotion
    remotion_ready = False
    if node_version:
        remotion_ready = bool(shutil.which("remotion") or shutil.which("npx"))

    # Check blender
    blender_version = check_command_version("blender", "--version")
    if blender_version and "Blender" in blender_version:
        blender_version = blender_version.split("\n")[0].strip()

    return {
        "python": {
            "available": True,
            "version": sys.version.split()[0],
        },
        "node": {
            "available": bool(node_version),
            "version": node_version or "Not found",
        },
        "npm": {
            "available": bool(npm_version),
            "version": npm_version or "Not found",
        },
        "ffmpeg": {
            "available": bool(ffmpeg_version),
            "version": ffmpeg_version or "Not found",
        },
        "edge_tts": {
            "available": edge_tts_installed,
            "version": "installed" if edge_tts_installed else "Not found",
        },
        "blender": {
            "available": bool(blender_version),
            "version": blender_version or "Not found",
        },
        "remotion_ready": remotion_ready,
        "video_capable": bool(node_version and ffmpeg_version),
        "audio_capable": bool(edge_tts_installed and ffmpeg_version),
        "blender_3d_capable": bool(blender_version),
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

    lines.append("------------------------------------------------------------")
    lines.append("Capabilities Summary:")
    lines.append(f"  - Long-Form Articles & Markdown : [READY] (Native Python)")
    lines.append(f"  - 3:4 Social Carousels (Pillow) : [READY] (Native Python)")
    lines.append(f"  - Neural Voiceover Generation   : [{'READY' if caps['audio_capable'] else 'DEGRADED (Requires edge-tts + ffmpeg)'}]")
    lines.append(f"  - Programmatic Video (Remotion) : [{'READY' if caps['video_capable'] else 'DEGRADED (Requires Node.js 20+ and ffmpeg)'}]")
    lines.append(f"  - 3D Assets & Mockups (Blender) : [{'READY' if caps.get('blender_3d_capable') else 'OPTIONAL (Requires Blender 4.2+ LTS)'}]")
    lines.append("============================================================")

    return "\n".join(lines)
