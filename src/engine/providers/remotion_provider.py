"""Remotion provider: isolated headless video rendering via the local CLI."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.engine.media_stager import MediaStageError, MediaStager
from src.engine.providers.base import ProviderError, RenderProvider, file_sha256, register

PROJECT_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_ENTRY_POINT = PROJECT_ROOT / "src" / "video" / "index.ts"
_DEFAULT_PUBLIC_DIR = PROJECT_ROOT / "public"


@register
class RemotionProvider(RenderProvider):
    name = "remotion"
    capability = "remotion"
    supports = frozenset({"video"})
    default_extension = "mp4"

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root or PROJECT_ROOT).resolve()
        self.stager = MediaStager(self.project_root)

    # ------------------------------------------------------------------
    # Path resolution
    # ------------------------------------------------------------------
    def _resolve_relative(self, value: str, *, label: str) -> Path:
        candidate = Path(value)
        resolved = (
            candidate.resolve()
            if candidate.is_absolute()
            else (self.project_root / candidate).resolve()
        )
        try:
            resolved.relative_to(self.project_root)
        except ValueError as exc:
            raise ProviderError(f"{label} escapes the project root: {resolved}") from exc
        return resolved

    def _entry_point(self, spec: Dict[str, Any]) -> Path:
        value = str(spec.get("entry_point") or "").strip()
        if not value:
            return _DEFAULT_ENTRY_POINT
        resolved = self._resolve_relative(value, label="entry_point")
        if not resolved.is_file():
            raise ProviderError(f"Remotion entry point not found: {resolved}")
        channel_slug = str(spec.get("channel_slug") or "").strip()
        if channel_slug:
            channel_dir = (self.project_root / "channels" / channel_slug).resolve()
            try:
                resolved.relative_to(channel_dir)
            except ValueError as exc:
                raise ProviderError(
                    f"entry_point must stay inside channels/{channel_slug}/: {resolved}"
                ) from exc
        return resolved

    def _public_dir(self, spec: Dict[str, Any]) -> Optional[Path]:
        value = str(spec.get("public_dir") or "").strip()
        if not value:
            return None
        resolved = self._resolve_relative(value, label="public_dir")
        if not resolved.is_dir():
            resolved.mkdir(parents=True, exist_ok=True)
        channel_slug = str(spec.get("channel_slug") or "").strip()
        if channel_slug:
            channel_dir = (self.project_root / "channels" / channel_slug).resolve()
            try:
                resolved.relative_to(channel_dir)
            except ValueError as exc:
                raise ProviderError(
                    f"public_dir must stay inside channels/{channel_slug}/: {resolved}"
                ) from exc
        return resolved

    def _media_manifest(self, spec: Dict[str, Any]) -> Optional[Path]:
        value = str(spec.get("media_manifest") or "").strip()
        if not value:
            return None
        resolved = self._resolve_relative(value, label="media_manifest")
        if not resolved.is_file():
            raise ProviderError(f"Media manifest not found: {resolved}")
        return resolved

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate(self, spec: Dict[str, Any]) -> List[str]:
        errors = super().validate(spec)
        errors.extend(self.check_required(spec, ["composition"]))

        composition = str(spec.get("composition") or "")
        if composition and not all(c.isalnum() or c in "-_" for c in composition):
            errors.append(f"invalid composition id '{composition}'")

        props = spec.get("props", {})
        if props is not None and not isinstance(props, dict):
            errors.append("props must be an object")

        try:
            entry = self._entry_point(spec)
            if not entry.exists():
                errors.append(f"Remotion entry point not found: {entry}")
        except ProviderError as exc:
            errors.append(str(exc))

        try:
            self._public_dir(spec)
        except ProviderError as exc:
            errors.append(str(exc))

        try:
            self._media_manifest(spec)
        except ProviderError as exc:
            errors.append(str(exc))

        fmt = str(spec.get("format") or "mp4").lower()
        if fmt not in ("mp4", "webm"):
            errors.append("format must be mp4 or webm")
        return errors

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------
    def render(self, spec: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
        errors = self.validate(spec)
        if errors:
            raise ProviderError("; ".join(errors))
        self._require(spec.get("channel_slug"))

        fmt = str(spec.get("format") or "mp4").lower()
        output = self.resolve_output(out_dir, spec.get("output"), "video")
        if output.suffix.lower() != f".{fmt}":
            output = output.with_suffix(f".{fmt}")

        entry_point = self._entry_point(spec)
        public_dir = self._public_dir(spec) or _DEFAULT_PUBLIC_DIR
        public_dir.mkdir(parents=True, exist_ok=True)

        props: Dict[str, Any] = dict(spec.get("props") or {})
        staged_mapping: Dict[str, str] = {}
        staged_report: Optional[Dict[str, Any]] = None
        manifest_path = self._media_manifest(spec)
        if manifest_path is not None:
            staged_report = self.stager.ensure(manifest_path, public_dir)
            staged_mapping = staged_report.get("mapping", {})

        if spec.get("normalize_media", True):
            props, replacements = self.stager.normalize_props(
                props,
                public_dir,
                mapping=staged_mapping,
                allow_legacy=bool(spec.get("stage_legacy_media", True)),
            )
        else:
            replacements = []

        props_path = Path(out_dir).resolve() / "remotion_props.json"
        props_path.write_text(
            json.dumps(props, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        cmd = [
            "npx",
            "remotion",
            "render",
            str(entry_point),
            str(spec["composition"]),
            str(output),
            f"--props={props_path}",
            "--log=error",
        ]
        if public_dir != _DEFAULT_PUBLIC_DIR:
            cmd.extend(["--public-dir", str(public_dir)])
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
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ProviderError(f"Remotion render timed out after {timeout}s") from exc

        if result.returncode != 0:
            tail = (result.stderr or result.stdout or "")[-1200:]
            raise ProviderError(
                f"Remotion render failed (code {result.returncode}): {tail}"
            )

        if not output.exists():
            raise ProviderError(
                f"Remotion finished but output was not produced: {output}"
            )

        payload = {
            "status": "success",
            "provider": self.name,
            "output_path": str(output),
            "composition": spec["composition"],
            "entry_point": str(entry_point),
            "public_dir": str(public_dir),
            "format": fmt,
            "file_size_bytes": output.stat().st_size,
            "sha256": file_sha256(output),
            "media_replacements": len(replacements),
        }
        if staged_report is not None:
            payload["media_staging"] = {
                "public_dir": staged_report["public_dir"],
                "files": len(staged_report["files"]),
            }
        return payload
