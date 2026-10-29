"""Remotion provider: isolated headless video rendering via the local CLI."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from src.engine.providers.base import ProviderError, RenderProvider, file_sha256, register

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_ENTRY_POINT = PROJECT_ROOT / "src" / "video" / "index.ts"


@register
class RemotionProvider(RenderProvider):
    name = "remotion"
    capability = "remotion"
    supports = frozenset({"video"})
    default_extension = "mp4"

    def validate(self, spec: Dict[str, Any]) -> List[str]:
        errors = super().validate(spec)
        errors.extend(self.check_required(spec, ["composition"]))

        composition = str(spec.get("composition") or "")
        if composition and not all(c.isalnum() or c in "-_" for c in composition):
            errors.append(f"invalid composition id '{composition}'")

        props = spec.get("props", {})
        if props is not None and not isinstance(props, dict):
            errors.append("props must be an object")

        if not _ENTRY_POINT.exists():
            errors.append(f"Remotion entry point not found: {_ENTRY_POINT}")

        fmt = str(spec.get("format") or "mp4").lower()
        if fmt not in ("mp4", "webm"):
            errors.append("format must be mp4 or webm")
        return errors

    def render(self, spec: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
        errors = self.validate(spec)
        if errors:
            raise ProviderError("; ".join(errors))
        self._require(spec.get("channel_slug"))

        fmt = str(spec.get("format") or "mp4").lower()
        output = self.resolve_output(out_dir, spec.get("output"), "video")
        if output.suffix.lower() != f".{fmt}":
            output = output.with_suffix(f".{fmt}")

        props_path = Path(out_dir).resolve() / "remotion_props.json"
        props_path.write_text(
            json.dumps(spec.get("props") or {}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        cmd = [
            "npx",
            "remotion",
            "render",
            str(_ENTRY_POINT),
            str(spec["composition"]),
            str(output),
            f"--props={props_path}",
            "--log=error",
        ]
        if spec.get("codec"):
            cmd.extend(["--codec", str(spec["codec"])])
        if spec.get("fps"):
            cmd.extend(["--fps", str(int(spec["fps"]))])
        if spec.get("duration_frames"):
            cmd.extend(["--frames", f"0-{max(0, int(spec['duration_frames']) - 1)}"])

        timeout = int(spec.get("timeout_seconds", 3600))
        try:
            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ProviderError(f"Remotion render timed out after {timeout}s") from exc

        if result.returncode != 0:
            tail = (result.stderr or result.stdout or "")[-1200:]
            raise ProviderError(f"Remotion render failed (code {result.returncode}): {tail}")

        if not output.exists():
            raise ProviderError(f"Remotion finished but output was not produced: {output}")

        return {
            "status": "success",
            "provider": self.name,
            "output_path": str(output),
            "composition": spec["composition"],
            "format": fmt,
            "file_size_bytes": output.stat().st_size,
            "sha256": file_sha256(output),
        }
