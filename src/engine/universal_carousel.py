"""Universal Carousel Engine for OmniPress MCP.

Processes declarative carousel recipes (JSON/YAML) and executes end-to-end:
1. Prepares background images (crops with top_bias, resizes, enhances contrast).
2. Renders branded slides complying with Rule 08 (contrast cards & safety strokes).
3. Uploads slide images to CDN/object storage (S3/R2/Catbox).
4. Publishes or schedules to social channels via PublishingShield and publisher adapters.
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image, ImageEnhance

from src.core.channel_manager import ChannelManager
from src.core.publishing_shield import PublishingShield
from src.engine.carousel_builder import CarouselBuilder
from src.utils.storage import BaseStorageProvider, get_default_storage_provider
from src.utils.sanitizer import sanitize_text

logger = logging.getLogger("omnipress.universal_carousel")

# Standard dimensions per aspect ratio
ASPECT_DIMENSIONS = {
    "3:4": (1080, 1440),
    "1:1": (1080, 1080),
    "9:16": (1080, 1920),
}


class UniversalCarouselEngine:
    """Universal, instruction-driven carousel generation and publishing engine."""

    def __init__(
        self,
        channel_manager: Optional[ChannelManager] = None,
        storage_provider: Optional[BaseStorageProvider] = None,
    ):
        self.channel_manager = channel_manager or ChannelManager()
        self.carousel_builder = CarouselBuilder(self.channel_manager)
        self.storage_provider = storage_provider

    def resolve_background_image(
        self,
        bg_reference: str,
        channel_slug: str,
        recipe_dir: Optional[Path] = None,
    ) -> Path:
        """Resolves background image path from relative or absolute paths, or channel raw media."""
        ref_path = Path(bg_reference)
        if ref_path.is_absolute() and ref_path.exists():
            return ref_path

        # 1. Check relative to recipe directory
        if recipe_dir:
            cand = (recipe_dir / ref_path).resolve()
            if cand.exists():
                return cand

        # 2. Check in channel's media/raw/ and media/visuals/
        channel_root = self.channel_manager.get_channel_dir(channel_slug)
        candidates = [
            channel_root / "media" / "raw" / ref_path.name,
            channel_root / "media" / "visuals" / ref_path.name,
            channel_root / "media" / ref_path.name,
            channel_root / "midias" / "raw" / ref_path.name,
            channel_root / "midias" / ref_path.name,
        ]
        for cand in candidates:
            if cand.exists():
                return cand.resolve()

        # If not found, return original path (let PIL raise explicit error)
        return ref_path.resolve()

    def prepare_background(
        self,
        src_path: Path,
        dst_path: Path,
        aspect_ratio: str = "3:4",
        top_bias: float = 0.20,
        contrast_boost: float = 1.15,
        color_boost: float = 1.0,
    ) -> Path:
        """Crops, resizes to exact target resolution and enhances archival contrast and color saturation."""
        target_size = ASPECT_DIMENSIONS.get(aspect_ratio, (1080, 1440))
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(src_path) as raw_img:
            # Handle alpha transparency safely to prevent black artifacts
            if raw_img.mode in ("RGBA", "LA") or (raw_img.mode == "P" and "transparency" in raw_img.info):
                rgba = raw_img.convert("RGBA")
                bg_composite = Image.new("RGBA", rgba.size, (10, 12, 16, 255))
                img = Image.alpha_composite(bg_composite, rgba).convert("RGB")
            elif raw_img.mode == "CMYK":
                img = raw_img.convert("RGB")
            else:
                img = raw_img.convert("RGB")

            w, h = img.size
            target_ratio = target_size[0] / target_size[1]
            img_ratio = w / h

            if img_ratio > target_ratio:
                new_w = int(h * target_ratio)
                left = (w - new_w) // 2
                img = img.crop((left, 0, left + new_w, h))
            else:
                new_h = int(w / target_ratio)
                top = int((h - new_h) * top_bias)
                top = max(0, min(top, h - new_h))
                img = img.crop((0, top, w, top + new_h))

            img = img.resize(target_size, Image.Resampling.LANCZOS)
            if contrast_boost != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast_boost)

            if color_boost != 1.0:
                color_enhancer = ImageEnhance.Color(img)
                img = color_enhancer.enhance(color_boost)

            img.save(dst_path, "JPEG", quality=95)
            return dst_path

    def load_recipe(self, recipe_input: Union[str, Path, Dict[str, Any]]) -> Tuple[Dict[str, Any], Optional[Path]]:
        """Loads and validates a recipe from a JSON file, path string, or dictionary."""
        if isinstance(recipe_input, dict):
            r_dir = recipe_input.get("_recipe_dir")
            return recipe_input, (Path(r_dir).resolve() if r_dir else None)

        recipe_path = Path(recipe_input).resolve()
        if not recipe_path.exists():
            raise FileNotFoundError(f"Carousel recipe file not found: {recipe_path}")

        try:
            data = json.loads(recipe_path.read_text(encoding="utf-8"))
            return data, recipe_path.parent
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in carousel recipe: {e}")

    def render_recipe_slides(
        self,
        recipe: Dict[str, Any],
        recipe_dir: Optional[Path] = None,
    ) -> List[Path]:
        """Prepares backgrounds and renders all slides for the recipe."""
        channel_slug = recipe.get("channel_slug") or self.channel_manager.get_active_channel().get("slug", "default")
        post_slug = recipe.get("post_slug", "untitled_carousel")
        aspect_ratio = recipe.get("aspect_ratio", "3:4")
        slides = recipe.get("slides", [])

        if not slides:
            raise ValueError("Carousel recipe must contain at least one slide in 'slides'.")

        # Output directory for prepared BGs and final slides
        carousels_dir = self.channel_manager.get_media_dir(channel_slug, "carousels")
        post_dir = carousels_dir / post_slug
        bgs_dir = post_dir / "prepared_bgs"
        bgs_dir.mkdir(parents=True, exist_ok=True)

        prepared_slides = []
        for idx, slide in enumerate(slides, start=1):
            bg_ref = slide.get("bg_image") or slide.get("bg_image_path")
            if not bg_ref:
                raise ValueError(f"Slide {idx} is missing 'bg_image' or 'bg_image_path'.")

            src_bg = self.resolve_background_image(bg_ref, channel_slug, recipe_dir)
            dst_bg = bgs_dir / f"bg_slide_{idx:02d}.jpg"

            top_bias = slide.get("top_bias", 0.20)
            contrast_boost = slide.get("contrast_boost", 1.15)
            color_boost = slide.get("color_boost", 1.0)
            self.prepare_background(
                src_path=src_bg,
                dst_path=dst_bg,
                aspect_ratio=aspect_ratio,
                top_bias=top_bias,
                contrast_boost=contrast_boost,
                color_boost=color_boost,
            )

            slide_dict = {
                "bg_image_path": str(dst_bg),
                "headline": slide.get("headline", ""),
                "body": slide.get("body", ""),
                "badge_text": slide.get("badge_text"),
                "gradient_start_ratio": slide.get("gradient_start_ratio", 0.46),
                "enable_text_card": slide.get("enable_text_card", True),
                "card_bg_alpha": slide.get("card_bg_alpha", 215),
                "stroke_width": slide.get("stroke_width", None),
            }
            if slide.get("swipe_str"):
                slide_dict["swipe_str"] = slide["swipe_str"]
            prepared_slides.append(slide_dict)

        rendered_paths = self.carousel_builder.build_carousel(
            channel_slug=channel_slug,
            post_slug=post_slug,
            slides_data=prepared_slides,
            aspect_ratio=aspect_ratio,
        )
        return rendered_paths

    def upload_slides(
        self,
        slide_paths: List[Path],
        output_json_path: Optional[Path] = None,
    ) -> List[str]:
        """Uploads slides to configured CDN/object storage provider."""
        provider = self.storage_provider or get_default_storage_provider()
        uploaded_urls = []

        for p in slide_paths:
            url = provider.upload_file(p)
            uploaded_urls.append(url)

        if output_json_path and uploaded_urls:
            output_json_path.parent.mkdir(parents=True, exist_ok=True)
            output_json_path.write_text(json.dumps(uploaded_urls, indent=2), encoding="utf-8")

        return uploaded_urls

    def schedule_or_publish(
        self,
        recipe: Dict[str, Any],
        media_urls: List[str],
        force_duplicate: bool = False,
    ) -> Dict[str, Any]:
        """Publishes or schedules the carousel using publisher adapters and PublishingShield."""
        from src.adapters.buffer_adapter import BufferPublisherAdapter

        channel_slug = recipe.get("channel_slug") or self.channel_manager.get_active_channel().get("slug", "default")
        publish_config = recipe.get("publish", {})
        if not publish_config:
            return {"skipped": True, "reason": "No publish block in recipe"}

        caption = publish_config.get("caption", "").strip()
        if not caption:
            return {"success": False, "error": "Publish config requires a non-empty 'caption'"}

        # Sanitize for privacy (Rule 01)
        clean_caption, _ = sanitize_text(caption)

        # Platform length validation (Rule 09)
        platforms = publish_config.get("platforms", ["instagram"])
        if "instagram" in platforms and len(clean_caption) > 2196:
            return {"success": False, "error": f"Caption exceeds Instagram 2,196 char limit ({len(clean_caption)})"}

        # Pre-flight duplicate check (Rule 09)
        is_dup, reason = PublishingShield.check_duplicate(
            channel_id=channel_slug,
            text=clean_caption,
            media_urls=media_urls,
            force=force_duplicate,
        )
        if is_dup and not force_duplicate:
            return {"success": False, "error": f"PublishingShield blocked duplicate post: {reason}"}

        adapter = BufferPublisherAdapter()
        if not adapter.is_configured():
            return {"success": False, "error": "Buffer adapter is not configured in environment"}

        schedule_time = publish_config.get("schedule_time")
        mode = publish_config.get("mode", "customScheduled" if schedule_time else "shareNow")

        res = adapter.queue_social_post(
            text=clean_caption,
            platforms=platforms,
            media_urls=media_urls,
            schedule_time=schedule_time,
            channel_slug=channel_slug,
            mode=mode,
        )

        if res.get("success"):
            PublishingShield.record_published(
                channel_id=channel_slug,
                text=clean_caption,
                media_urls=media_urls,
                provider="buffer",
                status="queued" if schedule_time else "published",
                response=res,
            )

        return res

    def execute_recipe(
        self,
        recipe_input: Union[str, Path, Dict[str, Any]],
        render: bool = True,
        upload: bool = False,
        schedule: bool = False,
        force_duplicate: bool = False,
    ) -> Dict[str, Any]:
        """Full pipeline execution orchestrator for a carousel recipe."""
        recipe, recipe_dir = self.load_recipe(recipe_input)
        channel_slug = recipe.get("channel_slug") or self.channel_manager.get_active_channel().get("slug", "default")
        post_slug = recipe.get("post_slug", "untitled_carousel")
        post_dir = self.channel_manager.get_media_dir(channel_slug, "carousels") / post_slug

        result = {
            "channel_slug": channel_slug,
            "post_slug": post_slug,
            "rendered_slides": [],
            "cdn_urls": [],
            "publish_result": None,
        }

        # Step 1: Render slides
        rendered_slides = []
        if render:
            rendered_slides = self.render_recipe_slides(recipe, recipe_dir)
            result["rendered_slides"] = [str(p) for p in rendered_slides]
        else:
            # Look for existing slides
            existing = sorted(post_dir.glob("slide_*.jpg"))
            if existing:
                rendered_slides = existing
                result["rendered_slides"] = [str(p) for p in existing]

        # Step 2: Upload slides to CDN
        cdn_urls = []
        urls_file = post_dir / "cdn_urls.json"
        if upload and rendered_slides:
            cdn_urls = self.upload_slides(rendered_slides, output_json_path=urls_file)
            result["cdn_urls"] = cdn_urls
        elif urls_file.exists():
            try:
                cdn_urls = json.loads(urls_file.read_text(encoding="utf-8"))
                result["cdn_urls"] = cdn_urls
            except Exception:
                pass

        # Step 3: Publish or schedule
        if schedule:
            if not cdn_urls and rendered_slides:
                # Auto-upload if not uploaded yet
                cdn_urls = self.upload_slides(rendered_slides, output_json_path=urls_file)
                result["cdn_urls"] = cdn_urls

            pub_res = self.schedule_or_publish(recipe, cdn_urls, force_duplicate=force_duplicate)
            result["publish_result"] = pub_res

        return result
