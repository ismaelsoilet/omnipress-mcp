"""OmniPress Agnostic Carousel Builder - Renders branded carousel slides for any channel."""

import textwrap
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from src.core.channel_manager import ChannelManager


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Converts a hex color (#RRGGBB) to an RGB tuple."""
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 3:
        hex_code = "".join(c * 2 for c in hex_code)
    try:
        return int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
    except Exception:
        return (212, 175, 55)  # Default gold


def wrap_text_by_pixel(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    """Dynamically wraps words so no line ever exceeds max_width pixels."""
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines


class CarouselBuilder:
    """
    Channel-agnostic slide layout engine.
    Renders high-contrast, perfectly-padded slides tailored to each channel's branding.
    """

    def __init__(self, channel_manager: Optional[ChannelManager] = None):
        self.channel_manager = channel_manager or ChannelManager()

    def render_slide(
        self,
        bg_image_path: Path,
        output_path: Path,
        channel_slug: str,
        headline: str,
        body: str = "",
        badge_text: Optional[str] = None,
        page_str: str = "01/05",
        swipe_str: str = "Deslize →",
        gradient_start_ratio: float = 0.46,
        aspect_ratio: str = "3:4",
        enable_text_card: bool = True,
        card_bg_alpha: int = 215,
        stroke_width: Optional[int] = None,
    ) -> Path:
        """Renders a single branded carousel slide with contrast and typography safety (Rule 08)."""
        channel = self.channel_manager.get_channel(channel_slug) or self.channel_manager.get_active_channel()
        branding = channel.get("branding", {})
        colors = branding.get("theme_colors", {})
        typography = branding.get("typography", {})

        primary_rgb = hex_to_rgb(colors.get("primary", "#D4AF37"))
        handle = branding.get("handle", "@canal")
        badge = badge_text or branding.get("badge_text", channel.get("name", "OMNIPRESS"))

        bold_font_path = typography.get("bold_font", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        reg_font_path = typography.get("regular_font", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

        img = Image.open(bg_image_path).convert("RGBA")
        w, h = img.size

        # Force target aspect ratio (3:4 or 1:1)
        target_ratio = 3 / 4 if aspect_ratio == "3:4" else 1.0
        current_ratio = w / h
        if current_ratio < target_ratio - 0.05:
            target_h = int(w / target_ratio)
            top = (h - target_h) // 2
            img = img.crop((0, top, w, top + target_h))
            w, h = img.size
        elif current_ratio > target_ratio + 0.05:
            target_w = int(h * target_ratio)
            left = (w - target_w) // 2
            img = img.crop((left, 0, left + target_w, h))
            w, h = img.size

        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Fonts
        font_badge = ImageFont.truetype(bold_font_path, size=max(20, int(w * 0.024)))
        font_head = ImageFont.truetype(bold_font_path, size=max(38, int(w * 0.046)))
        font_body = ImageFont.truetype(reg_font_path, size=max(28, int(w * 0.034)))
        font_foot = ImageFont.truetype(bold_font_path, size=max(20, int(w * 0.024)))

        # Dynamic Text Layout Pre-calculation (needed for gradient & safety card placement)
        margin_x = int(w * 0.065)
        max_text_w = w - (margin_x * 2)

        head_lines = wrap_text_by_pixel(headline, font_head, max_text_w, draw)
        body_lines = wrap_text_by_pixel(body, font_body, max_text_w, draw) if body else []

        line_h_head = int(font_head.size * 1.25)
        line_h_body = int(font_body.size * 1.35)

        total_h = len(head_lines) * line_h_head + 14 + len(body_lines) * line_h_body
        start_y = h - total_h - int(h * 0.11)

        # 1. Dark bottom gradient (starts before text begins to guarantee base contrast)
        grad_start = min(int(h * gradient_start_ratio), max(0, start_y - int(h * 0.06)))
        for y in range(grad_start, h):
            progress = (y - grad_start) / max(1, (h - grad_start))
            alpha = int(252 * (progress ** 0.85))
            draw.line([(0, y), (w, y)], fill=(8, 10, 14, min(252, alpha)))

        # 2. Top vignette for the badge
        for y in range(int(h * 0.13)):
            alpha = int(180 * (1 - (y / (h * 0.13))))
            draw.line([(0, y), (w, y)], fill=(8, 10, 14, min(180, alpha)))

        # 3. Top Badge (Pill container with dynamic font sizing)
        badge_content = f"• {badge.upper()} | {handle.upper()} •"
        bx, by = int(w * 0.06), int(h * 0.045)
        max_badge_w = w - (bx * 2) - 28
        badge_size = max(20, int(w * 0.024))
        font_badge = ImageFont.truetype(bold_font_path, size=badge_size)
        bbox_b = draw.textbbox((0, 0), badge_content, font=font_badge)
        bw, bh = bbox_b[2] - bbox_b[0], bbox_b[3] - bbox_b[1]
        while bw > max_badge_w and badge_size > 14:
            badge_size -= 1
            font_badge = ImageFont.truetype(bold_font_path, size=badge_size)
            bbox_b = draw.textbbox((0, 0), badge_content, font=font_badge)
            bw, bh = bbox_b[2] - bbox_b[0], bbox_b[3] - bbox_b[1]

        draw.rounded_rectangle(
            [bx - 14, by - 8, bx + bw + 14, by + bh + 8],
            radius=8,
            fill=(*primary_rgb, 235)
        )
        draw.text((bx, by), badge_content, fill=(10, 12, 16, 255), font=font_badge)

        # 4. Protective Opaque/Translucent Text Backdrop Card (Rule 08)
        # Guarantees 100% legibility over pure white or busy background images
        if enable_text_card:
            card_pad_x = int(w * 0.035)
            card_pad_y = int(h * 0.02)
            card_box = [
                margin_x - card_pad_x,
                start_y - card_pad_y,
                w - margin_x + card_pad_x,
                start_y + total_h + card_pad_y,
            ]
            draw.rounded_rectangle(
                card_box,
                radius=16,
                fill=(8, 10, 14, card_bg_alpha),
                outline=(*primary_rgb, 60),
                width=1,
            )

        # 5. Text Rendering with Safety Stroke
        calc_stroke_w = stroke_width if stroke_width is not None else max(2, int(w * 0.0025))
        stroke_color = (4, 5, 8, 255)

        curr_y = start_y
        for line in head_lines:
            draw.text(
                (margin_x, curr_y),
                line,
                fill=(255, 255, 255, 255),
                font=font_head,
                stroke_width=calc_stroke_w,
                stroke_fill=stroke_color,
            )
            curr_y += line_h_head

        curr_y += 12
        for line in body_lines:
            draw.text(
                (margin_x, curr_y),
                line,
                fill=(225, 230, 235, 255),
                font=font_body,
                stroke_width=max(1, calc_stroke_w - 1),
                stroke_fill=stroke_color,
            )
            curr_y += line_h_body

        # 6. Footer with Safety Stroke
        foot_y = h - int(h * 0.055)
        draw.text(
            (margin_x, foot_y),
            handle,
            fill=(*primary_rgb, 240),
            font=font_foot,
            stroke_width=1,
            stroke_fill=stroke_color,
        )

        right_text = f"{page_str}  {swipe_str}"
        bbox_r = draw.textbbox((0, 0), right_text, font=font_foot)
        rw = bbox_r[2] - bbox_r[0]
        draw.text(
            (w - margin_x - rw, foot_y),
            right_text,
            fill=(200, 205, 215, 220),
            font=font_foot,
            stroke_width=1,
            stroke_fill=stroke_color,
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        final = Image.alpha_composite(img, overlay).convert("RGB")
        final.save(output_path, quality=95)
        return output_path

    def build_carousel(
        self,
        channel_slug: str,
        post_slug: str,
        slides_data: List[Dict[str, Any]],
        aspect_ratio: str = "3:4"
    ) -> List[Path]:
        """
        Builds a complete multi-slide carousel for a given channel and post.
        Saves slides into channels/<channel_slug>/media/carousels/<post_slug>/
        """
        out_dir = self.channel_manager.get_media_dir(channel_slug, "carousels") / post_slug
        out_dir.mkdir(parents=True, exist_ok=True)

        total_pages = len(slides_data)
        generated_paths = []

        for idx, slide in enumerate(slides_data, start=1):
            page_str = f"{idx:02d}/{total_pages:02d}"
            out_file = out_dir / f"slide_{idx:02d}.jpg"
            
            swipe_text = slide.get("swipe_str", "Deslize →" if idx < total_pages else "Salve & Siga")
            
            bg_path = Path(slide["bg_image_path"])
            self.render_slide(
                bg_image_path=bg_path,
                output_path=out_file,
                channel_slug=channel_slug,
                headline=slide["headline"],
                body=slide.get("body", ""),
                badge_text=slide.get("badge_text"),
                page_str=page_str,
                swipe_str=swipe_text,
                gradient_start_ratio=slide.get("gradient_start_ratio", 0.46),
                aspect_ratio=aspect_ratio,
                enable_text_card=slide.get("enable_text_card", True),
                card_bg_alpha=slide.get("card_bg_alpha", 215),
                stroke_width=slide.get("stroke_width", None),
            )
            generated_paths.append(out_file)

        return generated_paths

    # Alias for backward compatibility with CLI and legacy callers
    render_carousel_deck = build_carousel
