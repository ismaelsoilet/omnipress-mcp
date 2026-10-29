"""Universal deploy engine: copies approved deliverables into public/ with a manifest."""

from __future__ import annotations

import datetime
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.core.channel_manager import ChannelManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class UniversalDeployEngine:
    """Publishes rendered files to a public directory without leaving the workspace."""

    def __init__(self, channel_manager: Optional[ChannelManager] = None):
        self.channel_manager = channel_manager or ChannelManager()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def deploy(
        self,
        files: List[Union[str, Path]],
        target_dir: Union[str, Path] = "public",
        manifest_name: str = "deploy_manifest.json",
    ) -> Dict[str, Any]:
        target = Path(target_dir)
        if not target.is_absolute():
            target = (PROJECT_ROOT / target).resolve()
        target.mkdir(parents=True, exist_ok=True)

        deployed = []
        for item in files:
            source = Path(item).resolve()
            if not source.is_file():
                raise FileNotFoundError(f"Deliverable not found: {source}")
            destination = target / source.name
            shutil.copy2(source, destination)
            deployed.append(
                {
                    "source": str(source),
                    "destination": str(destination),
                    "size_bytes": destination.stat().st_size,
                    "sha256": self._sha256(destination),
                }
            )

        manifest = {
            "status": "success",
            "engine": "universal_deploy",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "target_dir": str(target),
            "files": deployed,
        }
        manifest_path = target / manifest_name
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        manifest["manifest_path"] = str(manifest_path)
        return manifest
