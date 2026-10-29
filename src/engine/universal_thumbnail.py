"""Universal high-CTR thumbnail engine (Rule 15).

Renders 1920x1080 (or 1080x1920) thumbnails from a declarative recipe:
3-4 power words, titanic typography, heavy safety stroke, chiaroscuro isolation
on the left half and a completely clear YouTube duration death zone.
"""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import Image, ImageDraw

from src.core.channel_manager import ChannelManager
from src.core.schema_validator import validate as validate_schema
from src.engine.carousel_builder import hex_to_rgb, load_safe_font, wrap_text_by_pixel
from src.engine.rule15_validator import validate_thumbnail_recipe

logger = logging.getLogger("omnipress.universal_thumbnail")

ASPECT_DIMENSIONS = {"16:9": (1920, 1080), "9:16": (1080, 1920)}


class UniversalThumbnailEngine:
    """Deterministic, channel-agnostic thumbnail renderer."""

    def __init__(self, channel_manager: Optional[ChannelManager] = None):
        self.channel_manager = channel_manager or ChannelManager()

    # ------------------------------------------------------------------
    # Resolution helpers
    # ------------------------------------------------------------------
    def resolve_media(
        self,
        media: str,
        channel_slug: Optional[str] = None,
        recipe_dir: Optional[Path] = None,
    ) -> Path:
        candidate = Path(str(media))
        if candidate.is_absolute():
            return candidate
        if recipe_dir and (recipe_dir / candidate).is_file():
            return (recipe_dir / candidate).resolve()
        if channel_slug:
            channel_dir = self.channel_manager.get_channel_dir(channel_slug)
            for base in (channel_dir / "media" / "raw", channel_dir / "media" / "visuals", channel_dir):
                if (base / candidate).is_file():
                    return (base / candidate).resolve()
        return candidate.resolve()

    def output_dir(self, channel_slug: Optional[str], post_slug: str, recipe_dir: Optional[Path]) -> Path:
        if channel_slug and self.channel_manager.get_channel(channel_slug):
            out = self.channel_manager.get_channel_dir(channel_slug) / "media" / "thumbnails" / post_slug
        else:
            out = (recipe_dir or Path.cwd()) / "output_thumbnails" / post_slug
        out.mkdir(parents=True, exist_ok=True)
        return out

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    @staticmethod
    def _cover(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        target_w, target_h = size
        target_ratio = target_w / target_h
        w, h = img.size
        ratio = w / h
        if ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = int((h - new_h) * 0.28)
            img = img.crop((0, top, w, top + new_h))
        return img.resize(size, Image.Resampling.LANCZOS)

    @staticmethod
    def _chiaroscuro(canvas: Image.Image, text_area_ratio: float) -> Image.Image:
        w, h = canvas.size
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        limit = int(w * text_area_ratio)
        for x in range(limit):
            progress = x / max(1, limit - 1)
            alpha = int(245 * (1.0 - progress) ** 0.85)
            draw.line([(x, 0), (x, h)], fill=(4, 6, 10, alpha))
        return Image.alpha_composite(canvas, overlay)

    def _render(
        self,
        recipe: Dict[str, Any],
        media_path: Path,
        out_path: Path,
        theme: Dict[str, str],
    ) -> Path:
        aspect = str(recipe.get("aspect_ratio") or "16:9")
        size = ASPECT_DIMENSIONS.get(aspect, (1920, 1080))
        w, h = size

        with Image.open(media_path) as raw:
            base = raw.convert("RGB")
        canvas = self._cover(base, size).convert("RGBA")

        safe = recipe.get("safe_zones") or {}
        text_area_ratio = float(safe.get("text_area_ratio") or 0.55)
        canvas = self._chiaroscuro(canvas, text_area_ratio)

        draw = ImageDraw.Draw(canvas)
        typography = recipe.get("typography") or {}
        font_path = typography.get("font_path")
        headline_size = int(typography.get("headline_font_size") or 190)
        badge_size = int(typography.get("badge_font_size") or 56)
        stroke_width = int(typography.get("stroke_width") or 12)

        accent = hex_to_rgb(theme.get("primary") or "#3B82F6")
        highlight = hex_to_rgb(theme.get("highlight") or "#FACC15")
        text_rgb = hex_to_rgb(theme.get("text") or "#FFFFFF")
        stroke_rgb = (4, 5, 8)

        headline = str(recipe.get("headline") or "").strip()
        highlight_word = str(recipe.get("highlight_word") or "").strip()
        margin_x = int(w * 0.045)
        max_text_w = int(w * text_area_ratio) - margin_x * 2

        # Shrink titanic typography until it fits the left safe area.
        font_head = load_safe_font(font_path, size=headline_size, is_bold=True)
        lines = wrap_text_by_pixel(headline, font_head, max_text_w, draw)
        while headline_size > 80 and len(lines) * int(headline_size * 1.08) > int(h * 0.62):
            headline_size -= 8
            font_head = load_safe_font(font_path, size=headline_size, is_bold=True)
            lines = wrap_text_by_pixel(headline, font_head, max_text_w, draw)

        line_height = int(headline_size * 1.08)
        block_h = len(lines) * line_height
        start_y = int(h * 0.50) - block_h // 2

        # Badge (top-left authority seal)
        badge_text = str(recipe.get("badge_text") or "").strip()
        if badge_text:
            font_badge = load_safe_font(font_path, size=badge_size, is_bold=True)
            bbox = draw.textbbox((0, 0), badge_text.upper(), font=font_badge)
            bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            bx, by = margin_x, int(h * 0.055)
            draw.rounded_rectangle(
                [bx - 16, by - 10, bx + bw + 16, by + bh + 12],
                radius=10,
                fill=(*accent, 240),
            )
            draw.text((bx, by - 2), badge_text.upper(), fill=(*stroke_rgb, 255), font=font_badge)

        # Headline with word-level highlight
        curr_y = start_y
        for line in lines:
            words = line.split()
            cursor_x = margin_x
            for word in words:
                fill = (*highlight, 255) if highlight_word and word.strip(".,!?:;").lower() == highlight_word.lower() else (*text_rgb, 255)
                draw.text(
                    (cursor_x, curr_y),
                    word,
                    font=font_head,
                    fill=fill,
                    stroke_width=stroke_width,
                    stroke_fill=(*stroke_rgb, 255),
                )
                word_w = draw.textlength(word + " ", font=font_head)
                cursor_x += int(word_w)
            curr_y += line_height

        # Optional tagline under the headline (still >= 50px)
        tagline = str(recipe.get("tagline") or "").strip()
        if tagline:
            font_tag = load_safe_font(font_path, size=max(52, int(headline_size * 0.34)), is_bold=True)
            draw.text(
                (margin_x, curr_y + int(h * 0.02)),
                tagline,
                font=font_tag,
                fill=(*text_rgb, 255),
                stroke_width=max(4, stroke_width - 7),
                stroke_fill=(*stroke_rgb, 255),
            )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(out_path, "JPEG", quality=95)
        return out_path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def render_recipe(
        self,
        recipe: Union[str, Path, Dict[str, Any]],
        channel_slug: Optional[str] = None,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        recipe_dir: Optional[Path] = None
        if isinstance(recipe, (str, Path)):
            recipe_path = Path(recipe).resolve()
            if not recipe_path.is_file():
                raise FileNotFoundError(f"Thumbnail recipe not found: {recipe_path}")
            data = json.loads(recipe_path.read_text(encoding="utf-8"))
            recipe_dir = recipe_path.parent
        else:
            data = dict(recipe)

        validate_schema("thumbnail_recipe", data, source=str(recipe_dir or "<dict>"))
        rule15_errors = validate_thumbnail_recipe(data)
        if rule15_errors:
            raise ValueError("Rule 15 violations: " + "; ".join(rule15_errors))

        if validate_only:
            return {"status": "valid", "rule15": {"errors": [], "approved": True}}

        target_slug = channel_slug or data.get("channel_slug") or self.channel_manager.get_active_channel_slug()
        channel = self.channel_manager.get_channel(target_slug) or {}
        palette = ((channel.get("visual_identity") or {}).get("palette") or {})
        theme = {
            "primary": ((data.get("theme") or {}).get("primary") or palette.get("primary") or "#3B82F6"),
            "highlight": ((data.get("theme") or {}).get("highlight") or "#FACC15"),
            "text": ((data.get("theme") or {}).get("text") or palette.get("text") or "#FFFFFF"),
        }

        media_path = self.resolve_media(str(data.get("media") or ""), target_slug, recipe_dir)
        if not media_path.is_file():
            raise FileNotFoundError(f"Thumbnail media not found: {media_path}")

        post_slug = str(data.get("post_slug") or Path(str(data.get("output_name") or "thumbnail")).stem)
        out_dir = self.output_dir(target_slug, post_slug, recipe_dir)
        out_name = str(data.get("output_name") or "thumbnail.jpg")
        if Path(out_name).name != out_name:
            raise ValueError("output_name must not contain path separators")
        out_path = out_dir / out_name

        self._render(data, media_path, out_path, theme)

        manifest = {
            "status": "success",
            "engine": "universal_thumbnail",
            "channel_slug": target_slug,
            "output_path": str(out_path),
            "aspect_ratio": data.get("aspect_ratio") or "16:9",
            "headline": data.get("headline"),
            "rule15": {"approved": True, "errors": []},
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        manifest_path = out_dir / "thumbnail_manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["thumbnail_manifest"] = str(manifest_path)
        return manifest

    def mobile_previews(self, image_path: Path, widths: Optional[List[int]] = None) -> List[Path]:
        widths = widths or [120, 320]
        image_path = Path(image_path)
        preview_dir = image_path.parent / "previews"
        preview_dir.mkdir(parents=True, exist_ok=True)
        results: List[Path] = []
        with Image.open(image_path) as img:
            for width in widths:
                ratio = width / img.width
                height = max(1, int(img.height * ratio))
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                target = preview_dir / f"{image_path.stem}_{width}px{image_path.suffix}"
                resized.save(target, quality=90)
                results.append(target)
        return results
