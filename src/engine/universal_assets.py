"""Universal asset acquisition engine (public-domain archives + preparation)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from src.core.channel_manager import ChannelManager
from src.core.schema_validator import validate as validate_schema
from src.engine.providers.stock_asset_provider import StockAssetProvider
from src.engine.universal_carousel import UniversalCarouselEngine


class UniversalAssetsEngine:
    """Fetches allowlisted public-domain assets and prepares them for layouts."""

    def __init__(self, channel_manager: Optional[ChannelManager] = None):
        self.channel_manager = channel_manager or ChannelManager()
        self.provider = StockAssetProvider()

    def _output_dir(
        self,
        channel_slug: Optional[str],
        post_slug: str,
        recipe_dir: Optional[Path],
    ) -> Path:
        if channel_slug and self.channel_manager.get_channel(channel_slug):
            out = self.channel_manager.get_channel_dir(channel_slug) / "media" / "raw" / "assets" / post_slug
        else:
            out = (recipe_dir or Path.cwd()) / "output_assets" / post_slug
        out.mkdir(parents=True, exist_ok=True)
        return out

    def fetch(
        self,
        recipe: Union[str, Path, Dict[str, Any]],
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        recipe_dir: Optional[Path] = None
        if isinstance(recipe, (str, Path)):
            recipe_path = Path(recipe).resolve()
            if not recipe_path.is_file():
                raise FileNotFoundError(f"Asset recipe not found: {recipe_path}")
            data = json.loads(recipe_path.read_text(encoding="utf-8"))
            recipe_dir = recipe_path.parent
        else:
            data = dict(recipe)

        validate_schema("asset_recipe", data, source=str(recipe_dir or "<dict>"))
        target_slug = channel_slug or data.get("channel_slug") or self.channel_manager.get_active_channel_slug()
        post_slug = str(data.get("post_slug") or Path(str(data.get("output") or "asset")).stem)
        out_dir = self._output_dir(target_slug, post_slug, recipe_dir)

        spec = {
            "query": data["query"],
            "output": data.get("output") or "asset.jpg",
            "source_allowlist": data.get("source_allowlist"),
            "license": data.get("license"),
            "attribution": data.get("attribution"),
            "channel_slug": target_slug if self.channel_manager.get_channel(target_slug) else None,
        }
        return self.provider.render(spec, out_dir)

    fetch_recipe = fetch

    def prepare(
        self,
        source: Union[str, Path],
        output: Union[str, Path],
        aspect_ratio: str = "16:9",
        top_bias: float = 0.20,
        contrast_boost: float = 1.05,
        color_boost: float = 1.0,
    ) -> Dict[str, Any]:
        """Crops/resizes an asset to the requested aspect ratio."""
        engine = UniversalCarouselEngine(self.channel_manager)
        dst = Path(output).resolve()
        engine.prepare_background(
            src_path=Path(source).resolve(),
            dst_path=dst,
            aspect_ratio=aspect_ratio,
            top_bias=top_bias,
            contrast_boost=contrast_boost,
            color_boost=color_boost,
        )
        return {
            "status": "success",
            "engine": "universal_assets",
            "output_path": str(dst),
            "aspect_ratio": aspect_ratio,
            "file_size_bytes": dst.stat().st_size if dst.exists() else 0,
        }
