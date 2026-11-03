"""Universal media staging for Remotion public directories.

Remotion's ``staticFile()`` rejects absolute paths. OmniPress engines often
produce absolute media paths from a channel workspace, so this module copies
those files into a public directory and rewrites the props to relative paths.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

MEDIA_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".avif",
    ".mp4",
    ".webm",
    ".mov",
    ".mkv",
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".ogg",
    ".flac",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
}


class MediaStageError(RuntimeError):
    """Raised when a media path cannot be staged safely."""


class MediaStager:
    """Copy project media into a Remotion public directory.

    The stager is stateless between calls and safe to reuse. It rejects paths
    that escape the project root or the target public directory.
    """

    def __init__(self, project_root: Optional[Union[str, Path]] = None):
        self.project_root = Path(
            project_root or Path(__file__).resolve().parents[2]
        ).resolve()

    # ------------------------------------------------------------------
    # Path safety
    # ------------------------------------------------------------------
    @staticmethod
    def _is_relative_to(path: Path, base: Path) -> bool:
        try:
            path.relative_to(base)
            return True
        except ValueError:
            return False

    def _resolve_source(self, value: Union[str, Path]) -> Path:
        candidate = Path(str(value))
        if candidate.is_absolute():
            resolved = candidate.resolve()
        else:
            resolved = (self.project_root / candidate).resolve()
        if not resolved.is_file():
            raise MediaStageError(f"Media source not found: {resolved}")
        if not self._is_relative_to(resolved, self.project_root):
            raise MediaStageError(
                f"Media source escapes the project root: {resolved}"
            )
        return resolved

    def _resolve_public_dir(self, public_dir: Union[str, Path]) -> Path:
        candidate = Path(str(public_dir))
        if candidate.is_absolute():
            resolved = candidate.resolve()
        else:
            resolved = (self.project_root / candidate).resolve()
        if not self._is_relative_to(resolved, self.project_root):
            raise MediaStageError(
                f"Public directory escapes the project root: {resolved}"
            )
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

    def _resolve_target(self, public_dir: Path, target: Union[str, Path]) -> Tuple[Path, str]:
        relative = Path(str(target))
        if relative.is_absolute() or ".." in relative.parts:
            raise MediaStageError(f"Unsafe media target: {target}")
        destination = (public_dir / relative).resolve()
        if not self._is_relative_to(destination, public_dir):
            raise MediaStageError(f"Media target escapes public dir: {target}")
        return destination, relative.as_posix()

    # ------------------------------------------------------------------
    # Staging
    # ------------------------------------------------------------------
    @staticmethod
    def _needs_copy(source: Path, destination: Path) -> bool:
        if not destination.is_file():
            return True
        source_stat = source.stat()
        destination_stat = destination.stat()
        if source_stat.st_size != destination_stat.st_size:
            return True
        return destination_stat.st_mtime_ns < source_stat.st_mtime_ns

    def _load_manifest(self, manifest: Union[str, Path, Dict[str, Any], List[Any]]) -> List[Dict[str, Any]]:
        data: Any = manifest
        if isinstance(manifest, (str, Path)):
            manifest_path = Path(manifest)
            if not manifest_path.is_absolute():
                manifest_path = self.project_root / manifest_path
            if not manifest_path.is_file():
                raise MediaStageError(f"Media manifest not found: {manifest_path}")
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            entries = data.get("files", [])
        elif isinstance(data, list):
            entries = data
        else:
            raise MediaStageError("Media manifest must be an object or a list")
        if not isinstance(entries, list):
            raise MediaStageError("Media manifest 'files' must be a list")
        normalised: List[Dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise MediaStageError("Each media entry must be an object")
            source = entry.get("source")
            target = entry.get("target")
            if not source or not target:
                raise MediaStageError("Each media entry needs source and target")
            normalised.append({"source": str(source), "target": str(target)})
        return normalised

    def ensure(
        self,
        manifest: Union[str, Path, Dict[str, Any], List[Any]],
        public_dir: Union[str, Path],
    ) -> Dict[str, Any]:
        """Copy every manifest entry into the public directory.

        Returns a JSON-serialisable report with a source -> public-relative
        mapping that callers can use to rewrite props.
        """
        entries = self._load_manifest(manifest)
        public = self._resolve_public_dir(public_dir)
        staged: List[Dict[str, Any]] = []
        mapping: Dict[str, str] = {}

        for entry in entries:
            source = self._resolve_source(entry["source"])
            destination, relative = self._resolve_target(public, entry["target"])
            copied = False
            if self._needs_copy(source, destination):
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                copied = True
            mapping[str(source)] = relative
            try:
                relative_source = source.relative_to(self.project_root).as_posix()
            except ValueError:
                relative_source = None
            if relative_source:
                mapping[relative_source] = relative
            staged.append(
                {
                    "source": str(source),
                    "target": relative,
                    "destination": str(destination),
                    "copied": copied,
                    "size_bytes": destination.stat().st_size,
                }
            )

        return {
            "status": "success",
            "public_dir": str(public),
            "files": staged,
            "mapping": mapping,
        }

    # ------------------------------------------------------------------
    # Legacy absolute-path normalisation
    # ------------------------------------------------------------------
    @staticmethod
    def _is_remote_or_data(value: str) -> bool:
        return value.startswith(
            ("http://", "https://", "data:", "blob:", "file:")
        )

    @staticmethod
    def _safe_basename(value: Path) -> str:
        name = value.name or "asset"
        return "".join(
            char if char.isalnum() or char in "-_." else "_" for char in name
        )

    def _stage_legacy(
        self,
        source: Path,
        public: Path,
        mapping: Dict[str, str],
    ) -> str:
        digest = hashlib.sha256(str(source).encode("utf-8")).hexdigest()[:10]
        relative = f"_legacy/{digest}_{self._safe_basename(source)}"
        destination, relative = self._resolve_target(public, relative)
        if self._needs_copy(source, destination):
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        mapping[str(source)] = relative
        return relative

    def normalize_props(
        self,
        props: Any,
        public_dir: Union[str, Path],
        mapping: Optional[Dict[str, str]] = None,
        allow_legacy: bool = True,
    ) -> Tuple[Any, List[Dict[str, str]]]:
        """Rewrite absolute media path strings in props to public-relative paths."""
        public = self._resolve_public_dir(public_dir)
        known = dict(mapping or {})
        replacements: List[Dict[str, str]] = []

        def walk(value: Any) -> Any:
            if isinstance(value, dict):
                return {key: walk(item) for key, item in value.items()}
            if isinstance(value, list):
                return [walk(item) for item in value]
            if not isinstance(value, str) or not value:
                return value
            if self._is_remote_or_data(value):
                return value

            candidate = Path(value)
            if not candidate.is_absolute():
                relative = known.get(candidate.as_posix())
                if relative is not None:
                    replacements.append({"from": value, "to": relative})
                    return relative
                return value
            resolved = candidate.resolve()
            if not resolved.is_file():
                return value
            if resolved.suffix.lower() not in MEDIA_EXTENSIONS:
                return value
            if not self._is_relative_to(resolved, self.project_root):
                raise MediaStageError(
                    f"Media source escapes the project root: {resolved}"
                )

            relative = known.get(str(resolved))
            if relative is None:
                if not allow_legacy:
                    return value
                relative = self._stage_legacy(resolved, public, known)
            replacements.append({"from": value, "to": relative})
            return relative

        return walk(props), replacements

    # ------------------------------------------------------------------
    # Helpers for callers
    # ------------------------------------------------------------------
    @staticmethod
    def manifest_for_paths(
        entries: Iterable[Tuple[Union[str, Path], str]],
    ) -> Dict[str, Any]:
        return {
            "files": [
                {"source": str(source), "target": target}
                for source, target in entries
            ]
        }
