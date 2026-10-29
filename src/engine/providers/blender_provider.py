"""Blender provider: isolated headless execution of declarative 3D templates."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, List

from src.core.capabilities import resolve_blender_binary
from src.engine.providers.base import ProviderError, RenderProvider, file_sha256, register

_FORMAT_EXTENSIONS = {"png": "png", "webm": "webm", "mp4": "mp4", "glb": "glb"}


@register
class BlenderProvider(RenderProvider):
    name = "blender"
    capability = "blender"
    supports = frozenset({"still", "video", "3d"})
    default_extension = "png"

    def validate(self, spec: Dict[str, Any]) -> List[str]:
        errors = super().validate(spec)
        errors.extend(self.check_required(spec, ["script_path"]))

        script = Path(str(spec.get("script_path", "")))
        if spec.get("script_path") and not script.is_file():
            errors.append(f"template script not found: {script}")

        fmt = str(spec.get("format") or "png").lower()
        if fmt not in _FORMAT_EXTENSIONS:
            errors.append(f"unsupported format '{fmt}' (expected png, webm, mp4 or glb)")

        supported = [str(f) for f in (spec.get("supported_formats") or ["png"])]
        if fmt not in supported:
            errors.append(
                f"template does not support format '{fmt}' (supported: {', '.join(sorted(supported))})"
            )

        resolution = str(spec.get("resolution") or "1080x1080")
        parts = resolution.lower().split("x")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            errors.append(f"invalid resolution '{resolution}' (expected WIDTHxHEIGHT)")

        if fmt in ("webm", "mp4"):
            try:
                if float(spec.get("duration_seconds", 0)) <= 0:
                    errors.append("duration_seconds must be > 0 for video output")
            except (TypeError, ValueError):
                errors.append("duration_seconds must be a number")

        if spec.get("output_name") and Path(str(spec["output_name"])).name != str(spec["output_name"]):
            errors.append("output_name must not contain path separators")

        for key in (spec.get("params") or {}):
            if Path(str(key)).name != str(key) or not str(key).replace("_", "").isalnum():
                errors.append(f"invalid template parameter name '{key}'")
        return errors

    def render(self, spec: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
        errors = self.validate(spec)
        if errors:
            raise ProviderError("; ".join(errors))

        info = self._require(spec.get("channel_slug"))
        fmt = str(spec.get("format") or "png").lower()
        default_name = f"{Path(str(spec['script_path'])).parent.name}.{_FORMAT_EXTENSIONS[fmt]}"
        output = self.resolve_output(out_dir, spec.get("output_name"), Path(default_name).stem)
        if output.suffix.lower() != f".{_FORMAT_EXTENSIONS[fmt]}":
            output = output.with_suffix(f".{_FORMAT_EXTENSIONS[fmt]}")

        binary = str(spec.get("binary") or info.binary)
        if not Path(binary).is_file():
            binary = resolve_blender_binary(spec.get("channel_slug")) or binary

        cmd = [
            binary,
            "-b",
            "--factory-startup",
            "--python-exit-code",
            "1",
            "-noaudio",
            "-P",
            str(Path(spec["script_path"]).resolve()),
            "--",
            "--output",
            str(output),
            "--resolution",
            str(spec.get("resolution") or "1080x1080"),
            "--engine",
            str(spec.get("engine") or "BLENDER_EEVEE_NEXT"),
            "--samples",
            str(int(spec.get("samples", 32))),
        ]

        if fmt in ("webm", "mp4"):
            cmd.extend(
                [
                    "--format",
                    fmt,
                    "--fps",
                    str(int(spec.get("fps", 30))),
                    "--duration",
                    str(float(spec.get("duration_seconds", 1))),
                ]
            )

        for key, value in (spec.get("params") or {}).items():
            flag = f"--{str(key).replace('_', '-')}"
            if isinstance(value, bool):
                if value:
                    cmd.append(flag)
            elif value is not None:
                cmd.extend([flag, str(value)])

        timeout = int(spec.get("timeout_seconds", 300))
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired as exc:
            raise ProviderError(f"Blender render timed out after {timeout}s") from exc

        if result.returncode != 0:
            tail = (result.stderr or result.stdout or "")[-800:]
            raise ProviderError(f"Blender render failed (code {result.returncode}): {tail}")

        if not output.exists():
            raise ProviderError(f"Blender finished but output was not produced: {output}")

        return {
            "status": "success",
            "provider": self.name,
            "output_path": str(output),
            "format": fmt,
            "resolution": spec.get("resolution") or "1080x1080",
            "blender_version": info.version,
            "file_size_bytes": output.stat().st_size,
            "sha256": file_sha256(output),
        }
