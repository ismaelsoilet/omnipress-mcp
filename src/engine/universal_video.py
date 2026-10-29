"""Universal Remotion video engine (recipe -> rendered MP4/WebM)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from src.core.channel_manager import ChannelManager
from src.core.schema_validator import validate as validate_schema
from src.engine.providers.remotion_provider import RemotionProvider


class UniversalVideoEngine:
    """Renders Remotion compositions from declarative recipes."""

    def __init__(self, channel_manager: Optional[ChannelManager] = None):
        self.channel_manager = channel_manager or ChannelManager()
        self.provider = RemotionProvider()

    @staticmethod
    def _normalize_legacy_recipe(data: Dict[str, Any]) -> Dict[str, Any]:
        """Accepts the legacy intro_recipe.json shape and normalizes it."""
        if "composition" in data:
            return data
        if "composition_16x9" in data or "composition_9x16" in data:
            outputs = data.get("outputs") or {}
            composition = data.get("composition_16x9") or data.get("composition_9x16")
            return {
                "composition": composition,
                "props": data.get("props") or {},
                "output": outputs.get("video_16x9") or outputs.get("video_9x16"),
                "duration_frames": data.get("duration_frames"),
                "fps": data.get("fps"),
                "format": "mp4",
                "outputs": outputs,
            }
        return data

    def render_recipe(
        self,
        recipe: Union[str, Path, Dict[str, Any]],
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        recipe_dir: Optional[Path] = None
        if isinstance(recipe, (str, Path)):
            recipe_path = Path(recipe).resolve()
            if not recipe_path.is_file():
                raise FileNotFoundError(f"Video recipe not found: {recipe_path}")
            data = self._normalize_legacy_recipe(
                json.loads(recipe_path.read_text(encoding="utf-8"))
            )
            recipe_dir = recipe_path.parent
        else:
            data = self._normalize_legacy_recipe(dict(recipe))

        validate_schema("video_recipe", data, source=str(recipe_dir or "<dict>"))

        target_slug = channel_slug or data.get("channel_slug") or self.channel_manager.get_active_channel_slug()
        if self.channel_manager.get_channel(target_slug):
            out_dir = (
                self.channel_manager.get_channel_dir(target_slug)
                / "media"
                / "output"
                / str(data.get("episode_slug") or data["composition"])
            )
        else:
            out_dir = (recipe_dir or Path.cwd()) / "output_video" / str(data["composition"])
        out_dir.mkdir(parents=True, exist_ok=True)

        spec = {
            "composition": data["composition"],
            "props": data.get("props") or {},
            "output": data.get("output"),
            "format": data.get("format") or "mp4",
            "codec": data.get("codec"),
            "fps": data.get("fps"),
            "duration_frames": data.get("duration_frames"),
            "timeout_seconds": data.get("timeout_seconds") or 3600,
            "channel_slug": target_slug if self.channel_manager.get_channel(target_slug) else None,
        }
        result = self.provider.render(spec, out_dir)
        result["engine"] = "universal_video"
        result["channel_slug"] = target_slug
        return result
