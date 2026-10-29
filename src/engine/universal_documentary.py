"""Universal documentary scene engine.

Renders authentic documentary scene cards (never bare text tables) and emits a
Remotion-ready `episode_config.json`. Every scene requires a real visual asset;
scene text is always placed over the Rule 08 protective backdrop card.
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

logger = logging.getLogger("omnipress.universal_documentary")

ASPECT_DIMENSIONS = {"16:9": (1920, 1080), "9:16": (1080, 1920)}

_SCENE_TYPE_MAP = {
    "ken_burns": "ken-burns",
    "archive_photo": "ken-burns",
    "portrait": "ken-burns",
    "tactical_map": "ken-burns",
    "document_card": "document-reveal",
    "stat_card": "stat-counter",
    "closing_card": "channel-outro",
}


class UniversalDocumentaryEngine:
    """Deterministic documentary scene renderer + episode manifest builder."""

    def __init__(self, channel_manager: Optional[ChannelManager] = None):
        self.channel_manager = channel_manager or ChannelManager()

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------
    def resolve_media(
        self,
        media: str,
        channel_slug: Optional[str],
        recipe_dir: Optional[Path],
    ) -> Path:
        candidate = Path(str(media))
        if candidate.is_absolute():
            return candidate
        if recipe_dir and (recipe_dir / candidate).is_file():
            return (recipe_dir / candidate).resolve()
        if channel_slug:
            channel_dir = self.channel_manager.get_channel_dir(channel_slug)
            for base in (
                channel_dir / "media" / "raw",
                channel_dir / "media" / "visuals",
                channel_dir / "episodios",
                channel_dir,
            ):
                if (base / candidate).is_file():
                    return (base / candidate).resolve()
        return candidate.resolve()

    def output_dir(
        self,
        channel_slug: Optional[str],
        episode_slug: str,
        recipe_dir: Optional[Path],
    ) -> Path:
        if channel_slug and self.channel_manager.get_channel(channel_slug):
            out = (
                self.channel_manager.get_channel_dir(channel_slug)
                / "media"
                / "visuals"
                / "documentary"
                / episode_slug
            )
        else:
            out = (recipe_dir or Path.cwd()) / "output_documentary" / episode_slug
        (out / "scenes").mkdir(parents=True, exist_ok=True)
        return out

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    @staticmethod
    def _cover(img: Image.Image, size: Tuple[int, int], top_bias: float) -> Image.Image:
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
            top = int((h - new_h) * max(0.0, min(1.0, top_bias)))
            img = img.crop((0, top, w, top + new_h))
        return img.resize(size, Image.Resampling.LANCZOS)

    def _render_scene(
        self,
        scene: Dict[str, Any],
        media_path: Path,
        out_path: Path,
        aspect_ratio: str,
        theme: Dict[str, str],
        typography: Dict[str, str],
    ) -> Path:
        size = ASPECT_DIMENSIONS.get(aspect_ratio, (1920, 1080))
        w, h = size

        with Image.open(media_path) as raw:
            if raw.mode in ("RGBA", "LA") or (raw.mode == "P" and "transparency" in raw.info):
                base = Image.alpha_composite(
                    Image.new("RGBA", raw.size, (10, 14, 22, 255)), raw.convert("RGBA")
                ).convert("RGB")
            else:
                base = raw.convert("RGB")

        canvas = self._cover(
            base, size, float(scene.get("top_bias", 0.20))
        ).convert("RGBA")
        draw = ImageDraw.Draw(canvas)

        accent = hex_to_rgb(theme.get("accent") or theme.get("primary") or "#3B82F6")
        text_rgb = hex_to_rgb(theme.get("text") or "#FFFFFF")
        secondary_rgb = hex_to_rgb(theme.get("secondary_text") or "#CBD5E1")
        stroke_rgb = hex_to_rgb(theme.get("background") or "#04060A")
        card_rgb = hex_to_rgb(theme.get("card_background") or "#080A0E")

        # Bottom cinematic gradient (protects the card)
        gradient_start = int(h * 0.38)
        for y in range(gradient_start, h):
            progress = (y - gradient_start) / max(1, h - gradient_start)
            alpha = int(235 * (progress ** 0.9))
            draw.line([(0, y), (w, y)], fill=(*stroke_rgb, alpha))

        headline = str(scene.get("headline") or scene.get("overlay_text") or "").strip()
        subheadline = str(scene.get("subheadline") or "").strip()
        badge = str(scene.get("badge") or "").strip()
        scene_type = str(scene.get("type") or "ken_burns")

        margin_x = int(w * 0.07)
        max_text_w = w - margin_x * 2
        font_head = load_safe_font(typography.get("bold_font"), size=int(w * 0.045), is_bold=True)
        font_sub = load_safe_font(typography.get("regular_font"), size=int(w * 0.028), is_bold=False)
        font_badge = load_safe_font(typography.get("bold_font"), size=int(w * 0.020), is_bold=True)

        head_lines = wrap_text_by_pixel(headline, font_head, max_text_w, draw) if headline else []
        sub_lines = wrap_text_by_pixel(subheadline, font_sub, max_text_w, draw) if subheadline else []
        line_h_head = int(getattr(font_head, "size", 48) * 1.25)
        line_h_sub = int(getattr(font_sub, "size", 30) * 1.4)

        card_pad = int(h * 0.035)
        content_h = (
            (len(head_lines) * line_h_head)
            + (len(sub_lines) * line_h_sub)
            + (int(font_badge.size * 2.2) if badge else 0)
            + 24
        )

        if scene_type in ("stat_card", "closing_card"):
            card_top = (h - content_h) // 2 - card_pad
        else:
            card_top = h - content_h - int(h * 0.12) - card_pad * 2

        card_box = [
            margin_x - card_pad,
            card_top,
            w - margin_x + card_pad,
            card_top + content_h + card_pad * 2,
        ]
        draw.rounded_rectangle(
            card_box,
            radius=int(w * 0.012),
            fill=(*card_rgb, 232),
            outline=(*accent, 210),
            width=3,
        )

        curr_y = card_top + card_pad
        if badge:
            draw.text(
                (margin_x, curr_y),
                badge.upper(),
                font=font_badge,
                fill=(*accent, 255),
                stroke_width=2,
                stroke_fill=(*stroke_rgb, 255),
            )
            curr_y += int(font_badge.size * 2.2)

        for line in head_lines:
            draw.text(
                (margin_x, curr_y),
                line,
                font=font_head,
                fill=(*text_rgb, 255),
                stroke_width=max(2, int(w * 0.0025)),
                stroke_fill=(*stroke_rgb, 255),
            )
            curr_y += line_h_head

        curr_y += 10
        for line in sub_lines:
            draw.text(
                (margin_x, curr_y),
                line,
                font=font_sub,
                fill=(*secondary_rgb, 255),
                stroke_width=2,
                stroke_fill=(*stroke_rgb, 255),
            )
            curr_y += line_h_sub

        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(out_path, "JPEG", quality=95)
        return out_path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def execute_recipe(
        self,
        recipe: Union[str, Path, Dict[str, Any]],
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        recipe_dir: Optional[Path] = None
        if isinstance(recipe, (str, Path)):
            recipe_path = Path(recipe).resolve()
            if not recipe_path.is_file():
                raise FileNotFoundError(f"Documentary recipe not found: {recipe_path}")
            data = json.loads(recipe_path.read_text(encoding="utf-8"))
            recipe_dir = recipe_path.parent
        else:
            data = dict(recipe)

        validate_schema("documentary_recipe", data, source=str(recipe_dir or "<dict>"))

        target_slug = channel_slug or data.get("channel_slug") or self.channel_manager.get_active_channel_slug()
        channel = self.channel_manager.get_channel(target_slug) or {}
        vis = channel.get("visual_identity") or {}
        palette = vis.get("palette") or {}
        typography = vis.get("typography") or {}
        theme = {
            "accent": (data.get("theme") or {}).get("accent") or palette.get("accent") or palette.get("primary") or "#3B82F6",
            "primary": (data.get("theme") or {}).get("primary") or palette.get("primary") or "#3B82F6",
            "text": (data.get("theme") or {}).get("text") or palette.get("text") or "#FFFFFF",
            "secondary_text": (data.get("theme") or {}).get("secondary_text") or palette.get("secondary_text") or "#CBD5E1",
            "background": (data.get("theme") or {}).get("background") or palette.get("background") or "#04060A",
            "card_background": (data.get("theme") or {}).get("card_background") or palette.get("card_background") or "#080A0E",
        }

        episode_slug = str(data.get("episode_slug") or data.get("id") or "episode")
        aspect_ratio = str(data.get("aspect_ratio") or "16:9")
        out_dir = self.output_dir(target_slug, episode_slug, recipe_dir)
        manifest_mode = str(data.get("mode") or "render") == "manifest"

        rendered: List[Dict[str, Any]] = []
        cursor = 0.0
        for index, scene in enumerate(data.get("scenes") or [], start=1):
            media = str(scene.get("media") or "").strip()
            if not media:
                raise ValueError(
                    f"Scene {scene.get('id', index)} has no media. Documentary scenes must never be bare text tables."
                )
            media_path = self.resolve_media(media, target_slug, recipe_dir)
            if not media_path.is_file():
                raise FileNotFoundError(f"Scene media not found: {media_path}")

            scene_id = str(scene.get("id") or f"scene_{index:02d}")
            out_path = out_dir / "scenes" / f"{index:02d}_{scene_id}.jpg"
            if not manifest_mode:
                self._render_scene(
                    scene, media_path, out_path, aspect_ratio, theme, typography
                )
            scene_media = str(out_path) if not manifest_mode else str(media_path)

            duration = float(scene.get("duration_seconds") or 6.0)
            start = float(scene.get("start_seconds", cursor))
            camera = scene.get("camera") or "slow_zoom_in"
            transition = scene.get("transition") or "cut"
            rendered.append(
                {
                    "id": scene_id,
                    "type": _SCENE_TYPE_MAP.get(str(scene.get("type")), "ken-burns"),
                    "sourceType": scene.get("type"),
                    "mediaSrc": scene_media,
                    "durationInSeconds": duration,
                    "startInSeconds": start,
                    "headline": scene.get("headline", ""),
                    "subheadline": scene.get("subheadline", ""),
                    "badge": scene.get("badge", ""),
                    "cameraDirection": {
                        "slow_zoom_in": "zoom-in",
                        "slow_zoom_out": "zoom-out",
                        "pan_left": "pan-left",
                        "pan_right": "pan-right",
                        "static": "subtle-zoom",
                    }.get(camera, "zoom-in"),
                    "transitionType": {
                        "cut": "fade",
                        "whip_pan": "whip-pan",
                        "flash": "shutter-flash",
                        "dissolve": "cross-dissolve",
                    }.get(transition, "fade"),
                }
            )
            cursor = max(cursor, start + duration)

        captions = data.get("captions")
        if isinstance(captions, str) and captions:
            caption_path = self.resolve_media(captions, target_slug, recipe_dir)
            captions_data = json.loads(caption_path.read_text(encoding="utf-8")) if caption_path.is_file() else {}
        elif isinstance(captions, dict):
            captions_data = captions
        else:
            captions_data = {}

        audio = data.get("audio") or {}
        episode_config = {
            "id": episode_slug,
            "title": data.get("title") or episode_slug,
            "channelSlug": target_slug,
            "language": data.get("language") or channel.get("language") or "pt",
            "theme": theme,
            "backgroundMusicSrc": audio.get("soundtrack", ""),
            "backgroundMusicVolume": audio.get("soundtrack_volume", 0.16),
            "scenes": rendered,
            "captions": captions_data,
            "voiceovers": (
                [audio["voiceover"]] if isinstance(audio.get("voiceover"), dict) else []
            ),
            "generatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        config_path = out_dir / str(
            (data.get("outputs") or {}).get("episode_config") or "episode_config.json"
        )
        config_path.write_text(
            json.dumps(episode_config, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        return {
            "status": "success",
            "engine": "universal_documentary",
            "channel_slug": target_slug,
            "episode_slug": episode_slug,
            "scenes_rendered": 0 if manifest_mode else len(rendered),
            "mode": "manifest" if manifest_mode else "render",
            "scenes": [item["mediaSrc"] for item in rendered],
            "episode_config": str(config_path),
            "total_duration_seconds": round(cursor, 3),
        }

    # Alias for API symmetry with the other engines.
    render_recipe = execute_recipe
