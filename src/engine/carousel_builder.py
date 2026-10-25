"""OmniPress Agnostic Carousel Builder - Renders branded carousel slides for any channel.

Supports 4 distinct visual presets:
1. classic_card: Rule 08 protective translucent backdrop card over archival background image.
2. tweet_card: Social-proof style (Thiago Ramos) with avatar, verified badge, handle, bold headline and rounded image frame.
3. minimal_dark: Minimalist dark-mode editorial (Rhaj Teixeira) with serif typography, step numbers, and UI mockups.
4. split_editorial: Corporate/GovTech authority (Portal da Reforma Tributária) with top photo, circular avatar cutout, square bullets (■), and watermark.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
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


def load_safe_font(font_path: Optional[str], size: int, is_bold: bool = False) -> Any:
    """Safely loads a TrueType font with cross-platform fallbacks (Linux, macOS, Windows) and default fallback."""
    candidates = []
    if font_path:
        candidates.append(font_path)

    if is_bold:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ])
    else:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ])

    for path in candidates:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue

    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def load_font_by_family(
    family: str = "sans",
    size: int = 24,
    is_bold: bool = False,
    custom_path: Optional[str] = None
) -> Any:
    """Safely loads a TrueType font for sans, serif, or mono font families."""
    if custom_path and Path(custom_path).is_file():
        try:
            return ImageFont.truetype(custom_path, size=size)
        except Exception:
            pass

    fam = family.lower()
    candidates = []
    if "serif" in fam:
        if is_bold:
            candidates.extend([
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                "/usr/share/fonts/dejavu/DejaVuSerif-Bold.ttf",
                "/System/Library/Fonts/Times.ttc",
                "/System/Library/Fonts/Supplemental/Georgia.ttf",
                "C:/Windows/Fonts/georgiab.ttf",
                "C:/Windows/Fonts/timesbd.ttf",
            ])
        else:
            candidates.extend([
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                "/usr/share/fonts/dejavu/DejaVuSerif.ttf",
                "/System/Library/Fonts/Times.ttc",
                "/System/Library/Fonts/Supplemental/Georgia.ttf",
                "C:/Windows/Fonts/georgia.ttf",
                "C:/Windows/Fonts/times.ttf",
            ])
    elif "mono" in fam:
        if is_bold:
            candidates.extend([
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
                "/usr/share/fonts/truetype/ubuntu/UbuntuSansMono-Bold.ttf",
                "/System/Library/Fonts/Menlo.ttc",
                "C:/Windows/Fonts/consola.ttf",
            ])
        else:
            candidates.extend([
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                "/usr/share/fonts/truetype/ubuntu/UbuntuSansMono.ttf",
                "/System/Library/Fonts/Menlo.ttc",
                "C:/Windows/Fonts/consola.ttf",
            ])
    else:  # Sans default
        return load_safe_font(custom_path, size=size, is_bold=is_bold)

    for p in candidates:
        if Path(p).is_file():
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                continue

    return load_safe_font(custom_path, size=size, is_bold=is_bold)


def wrap_text_by_pixel(text: str, font: Any, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    """Dynamically wraps words so no line ever exceeds max_width pixels, preserving explicit paragraph breaks."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = normalized.split("\n")
    lines = []
    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean:
            lines.append("")
            continue
        words = p_clean.split(" ")
        current_line = []
        for word in words:
            if not word:
                continue
            test_line = " ".join(current_line + [word]) if current_line else word
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
    Renders high-contrast, perfectly-padded slides tailored to each channel's branding and layout preset.
    """

    def __init__(self, channel_manager: Optional[ChannelManager] = None):
        self.channel_manager = channel_manager or ChannelManager()

    # -------------------------------------------------------------------------
    # Helper Vector Components
    # -------------------------------------------------------------------------

    def _draw_verified_badge(self, draw: ImageDraw.ImageDraw, x: int, y: int, diameter: int = 24) -> None:
        """Draws Twitter/Instagram blue verified checkmark badge."""
        blue_color = (29, 155, 240, 255)  # Twitter blue #1D9BF0
        draw.ellipse([x, y, x + diameter, y + diameter], fill=blue_color)
        p1 = (x + int(diameter * 0.25), y + int(diameter * 0.50))
        p2 = (x + int(diameter * 0.45), y + int(diameter * 0.70))
        p3 = (x + int(diameter * 0.78), y + int(diameter * 0.32))
        draw.line([p1, p2, p3], fill=(255, 255, 255, 255), width=max(2, int(diameter * 0.10)))

    def _draw_search_bar_mockup(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        width: int,
        height: int,
        query: str,
        font: Any,
        bg_color: Tuple[int, int, int, int] = (24, 26, 32, 255),
        border_color: Tuple[int, int, int, int] = (70, 75, 85, 255),
        text_color: Tuple[int, int, int, int] = (240, 242, 245, 255),
    ) -> None:
        """Renders an interactive search bar input mockup (Rhaj Teixeira style)."""
        radius = height // 2
        draw.rounded_rectangle([x, y, x + width, y + height], radius=radius, fill=bg_color, outline=border_color, width=2)

        # Query text
        text_x = x + int(height * 0.45)
        bbox = draw.textbbox((0, 0), query, font=font)
        text_h = bbox[3] - bbox[1]
        text_y = y + (height - text_h) // 2
        draw.text((text_x, text_y), query, fill=text_color, font=font)

        # Search icon (magnifying glass)
        icon_cx = x + width - int(height * 0.45)
        icon_cy = y + height // 2
        icon_r = int(height * 0.16)
        draw.ellipse([icon_cx - icon_r, icon_cy - icon_r - 2, icon_cx + icon_r, icon_cy + icon_r - 2], outline=(180, 185, 195, 255), width=2)
        draw.line(
            [(icon_cx + int(icon_r * 0.7), icon_cy + int(icon_r * 0.7) - 2), (icon_cx + icon_r + 5, icon_cy + icon_r + 3)],
            fill=(180, 185, 195, 255),
            width=2
        )

        # Clear '×' icon
        clear_x = x + width - int(height * 0.95)
        draw.line([(clear_x - 6, y + height // 2 - 6), (clear_x + 6, y + height // 2 + 6)], fill=(120, 125, 135, 255), width=2)
        draw.line([(clear_x - 6, y + height // 2 + 6), (clear_x + 6, y + height // 2 - 6)], fill=(120, 125, 135, 255), width=2)

    def _draw_circular_avatar(
        self,
        base_img: Image.Image,
        avatar_path: Optional[Union[str, Path]],
        x: int,
        y: int,
        size: int,
        fallback_initials: str = "OP",
        primary_rgb: Tuple[int, int, int] = (59, 130, 246),
        border_color: Optional[Tuple[int, int, int]] = None
    ) -> None:
        """Paints a circular avatar image or fallback initials circle."""
        resolved = Path(avatar_path) if avatar_path else None
        if resolved and resolved.is_file():
            try:
                with Image.open(resolved) as raw_av:
                    av_img = raw_av.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
                mask = Image.new("L", (size, size), 0)
                draw_m = ImageDraw.Draw(mask)
                draw_m.ellipse((0, 0, size, size), fill=255)
                base_img.paste(av_img, (x, y), mask)
                if border_color:
                    draw_b = ImageDraw.Draw(base_img)
                    draw_b.ellipse([x, y, x + size, y + size], outline=(*border_color, 255), width=2)
                return
            except Exception:
                pass

        # Fallback circle with initials
        draw = ImageDraw.Draw(base_img)
        draw.ellipse([x, y, x + size, y + size], fill=(*primary_rgb, 255))
        f_init = load_safe_font(None, size=max(14, int(size * 0.42)), is_bold=True)
        init_str = fallback_initials[:2].upper()
        bbox = draw.textbbox((0, 0), init_str, font=f_init)
        iw, ih = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x + (size - iw) // 2, y + (size - ih) // 2 - 2), init_str, fill=(255, 255, 255, 255), font=f_init)

    def _draw_rounded_image(
        self,
        base_img: Image.Image,
        src_path: Union[str, Path],
        box: Tuple[int, int, int, int],
        radius: int = 18,
        border_color: Optional[Tuple[int, int, int, int]] = (226, 232, 240, 255)
    ) -> None:
        """Crops, resizes, and pastes an image inside a rounded rectangle container."""
        src_file = Path(src_path)
        if not src_file.is_file():
            return

        target_w = box[2] - box[0]
        target_h = box[3] - box[1]
        if target_w <= 0 or target_h <= 0:
            return

        with Image.open(src_file) as raw_img:
            img = raw_img.convert("RGBA")
            # Aspect crop
            curr_ratio = img.width / img.height
            target_ratio = target_w / target_h
            if curr_ratio > target_ratio:
                new_w = int(img.height * target_ratio)
                left = (img.width - new_w) // 2
                img = img.crop((left, 0, left + new_w, img.height))
            else:
                new_h = int(img.width / target_ratio)
                top = (img.height - new_h) // 2
                img = img.crop((0, top, img.width, top + new_h))
            img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        mask = Image.new("L", (target_w, target_h), 0)
        draw_m = ImageDraw.Draw(mask)
        draw_m.rounded_rectangle([0, 0, target_w, target_h], radius=radius, fill=255)
        base_img.paste(img, (box[0], box[1]), mask)

        if border_color:
            draw_b = ImageDraw.Draw(base_img)
            draw_b.rounded_rectangle([box[0], box[1], box[2], box[3]], radius=radius, outline=border_color, width=1)

    # -------------------------------------------------------------------------
    # Preset Renderers
    # -------------------------------------------------------------------------

    def _render_minimal_dark(
        self,
        output_path: Path,
        w: int,
        h: int,
        headline: str,
        body: str,
        page_str: str,
        swipe_str: str,
        channel_data: Dict[str, Any],
        slide_data: Dict[str, Any]
    ) -> Path:
        """Preset B: Minimalist Dark Editorial (Rhaj Teixeira style)."""
        vis_id = channel_data.get("visual_identity", {})
        pal = vis_id.get("palette", {})
        bg_color = hex_to_rgb(slide_data.get("background") or pal.get("background", "#08080A"))

        img = Image.new("RGBA", (w, h), (*bg_color, 255))
        draw = ImageDraw.Draw(img)

        margin_x = int(w * 0.08)
        max_w = w - (margin_x * 2)

        # Serif fonts
        font_serif_head = load_font_by_family("serif", size=int(w * 0.046), is_bold=True)
        font_serif_body = load_font_by_family("serif", size=int(w * 0.034), is_bold=False)
        font_serif_step = load_font_by_family("serif", size=int(w * 0.038), is_bold=True)
        font_foot = load_font_by_family("sans", size=int(w * 0.022), is_bold=False)

        step_number = slide_data.get("step_number") or ""
        curr_y = int(h * 0.22)

        if step_number:
            draw.text((margin_x, curr_y), step_number, fill=(255, 255, 255, 255), font=font_serif_step)
            curr_y += int(w * 0.07)

        # Headline
        head_lines = wrap_text_by_pixel(headline, font_serif_head, max_w, draw)
        for line in head_lines:
            draw.text((margin_x, curr_y), line, fill=(255, 255, 255, 255), font=font_serif_head)
            curr_y += int(font_serif_head.size * 1.35)

        curr_y += int(h * 0.03)

        # Body
        if body:
            body_lines = wrap_text_by_pixel(body, font_serif_body, max_w, draw)
            for line in body_lines:
                draw.text((margin_x, curr_y), line, fill=(215, 220, 230, 255), font=font_serif_body)
                curr_y += int(font_serif_body.size * 1.45)

        # UI Mockup (Search bar / UI pill)
        ui_mockup = slide_data.get("ui_mockup") or {}
        if ui_mockup and ui_mockup.get("type") == "search_bar":
            query = ui_mockup.get("query", headline)
            bar_w = min(int(w * 0.84), max_w)
            bar_h = int(h * 0.065)
            bar_x = (w - bar_w) // 2
            bar_y = max(curr_y + int(h * 0.06), int(h * 0.62))
            font_query = load_font_by_family("sans", size=max(14, int(bar_h * 0.36)), is_bold=False)
            self._draw_search_bar_mockup(draw, bar_x, bar_y, bar_w, bar_h, query, font_query)

        # Footer
        handle = channel_data.get("branding", {}).get("handle", "@seuperfil")
        foot_y = h - int(h * 0.05)
        draw.text((margin_x, foot_y), handle, fill=(120, 130, 145, 220), font=font_foot)
        r_text = f"{page_str}   {swipe_str}"
        bbox_r = draw.textbbox((0, 0), r_text, font=font_foot)
        draw.text((w - margin_x - (bbox_r[2] - bbox_r[0]), foot_y), r_text, fill=(120, 130, 145, 220), font=font_foot)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(output_path, quality=95)
        return output_path

    def _render_tweet_card(
        self,
        output_path: Path,
        w: int,
        h: int,
        headline: str,
        body: str,
        page_str: str,
        swipe_str: str,
        channel_data: Dict[str, Any],
        slide_data: Dict[str, Any]
    ) -> Path:
        """Preset A: Social Proof & Tweet Card Mockup (Thiago Ramos style)."""
        vis_id = channel_data.get("visual_identity", {})
        pal = vis_id.get("palette", {})
        bg_color = hex_to_rgb(slide_data.get("background") or pal.get("background", "#FFFFFF"))
        is_dark = bg_color[0] < 50

        img = Image.new("RGBA", (w, h), (*bg_color, 255))
        draw = ImageDraw.Draw(img)

        margin_x = int(w * 0.075)
        max_w = w - (margin_x * 2)

        # Author header
        auth_data = slide_data.get("author") or vis_id.get("author", {})
        author_name = auth_data.get("name") or channel_data.get("name", "Autor")
        handle = auth_data.get("handle") or channel_data.get("branding", {}).get("handle", "@autor")
        avatar_path = auth_data.get("avatar_path")
        if avatar_path and not Path(avatar_path).is_file():
            ch_p = channel_data.get("path")
            if ch_p and (Path(ch_p) / avatar_path).is_file():
                avatar_path = str(Path(ch_p) / avatar_path)
            elif (Path("channels") / channel_data.get("slug", "") / avatar_path).is_file():
                avatar_path = str(Path("channels") / channel_data.get("slug", "") / avatar_path)

        is_verified = auth_data.get("verified", True)

        start_y = int(h * 0.12)
        avatar_size = int(w * 0.10)
        border_c = hex_to_rgb(pal.get("border", "#E0DFDC"))
        self._draw_circular_avatar(img, avatar_path, margin_x, start_y, avatar_size, fallback_initials=author_name, border_color=border_c)

        # Name and Verified badge
        text_start_x = margin_x + avatar_size + int(w * 0.03)
        font_name = load_font_by_family("sans", size=int(w * 0.038), is_bold=True)
        font_handle = load_font_by_family("sans", size=int(w * 0.026), is_bold=False)

        name_color = (255, 255, 255, 255) if is_dark else (15, 23, 42, 255)
        handle_color = (148, 163, 184, 255) if is_dark else (100, 116, 139, 255)

        draw.text((text_start_x, start_y + int(avatar_size * 0.08)), author_name, fill=name_color, font=font_name)
        if is_verified:
            bbox_n = draw.textbbox((0, 0), author_name, font=font_name)
            badge_x = text_start_x + (bbox_n[2] - bbox_n[0]) + 10
            badge_y = start_y + int(avatar_size * 0.10)
            self._draw_verified_badge(draw, badge_x, badge_y, diameter=int(w * 0.032))

        draw.text((text_start_x, start_y + int(avatar_size * 0.55)), handle, fill=handle_color, font=font_handle)

        curr_y = start_y + avatar_size + int(h * 0.04)

        # Headline
        clean_headline = re.sub(r'[\U00010000-\U0010ffff]', '', headline)
        clean_headline = re.sub(r'[\u2600-\u27bf]', '', clean_headline)
        clean_headline = re.sub(r'[\ufe00-\ufe0f]', '', clean_headline).strip()

        font_head = load_font_by_family("sans", size=int(w * 0.046), is_bold=True)
        head_lines = wrap_text_by_pixel(clean_headline, font_head, max_w, draw)
        for line in head_lines:
            draw.text((margin_x, curr_y), line, fill=name_color, font=font_head)
            curr_y += int(font_head.size * 1.30)

        curr_y += int(h * 0.02)

        # Body/Lead
        if body:
            clean_body = re.sub(r'[\U00010000-\U0010ffff]', '', body)
            clean_body = re.sub(r'[\u2600-\u27bf]', '', clean_body)
            clean_body = re.sub(r'[\ufe00-\ufe0f]', '', clean_body)
            clean_body = re.sub(r'[\u200d]', '', clean_body).strip()

            font_body = load_font_by_family("sans", size=int(w * 0.031), is_bold=False)
            font_body_bold = load_font_by_family("sans", size=int(w * 0.031), is_bold=True)
            body_color = (226, 232, 240, 255) if is_dark else (30, 41, 59, 255)
            mito_color = (248, 113, 113, 255) if is_dark else (220, 38, 38, 255)
            verdade_color = (52, 211, 153, 255) if is_dark else (5, 150, 105, 255)
            accent_rgb = hex_to_rgb(pal.get("accent", "#0A66C2"))

            paragraphs = clean_body.replace("\r\n", "\n").replace("\r", "\n").split("\n")
            for p in paragraphs:
                clean_p = p.strip()
                if not clean_p:
                    curr_y += int(font_body.size * 1.10)
                    continue

                if clean_p.startswith("MITO:"):
                    dot_color = mito_color
                    prefix = "MITO: "
                    prefix_color = mito_color
                    content = clean_p[5:].lstrip()
                elif clean_p.startswith("VERDADE:"):
                    dot_color = verdade_color
                    prefix = "VERDADE: "
                    prefix_color = verdade_color
                    content = clean_p[8:].lstrip()
                elif len(clean_p) >= 3 and clean_p[0].isdigit() and clean_p[1:3] in (". ", ") "):
                    dot_color = None
                    prefix = clean_p[:3]
                    prefix_color = (*accent_rgb, 255)
                    content = clean_p[3:].lstrip()
                else:
                    dot_color = None
                    prefix = ""
                    prefix_color = body_color
                    content = clean_p

                text_x = margin_x
                if dot_color:
                    dot_d = int(font_body.size * 0.40)
                    dot_y = curr_y + int(font_body.size * 0.42)
                    draw.ellipse([margin_x, dot_y, margin_x + dot_d, dot_y + dot_d], fill=dot_color)
                    text_x = margin_x + dot_d + 12

                prefix_w = 0
                if prefix:
                    draw.text((text_x, curr_y), prefix, fill=prefix_color, font=font_body_bold)
                    bbox = draw.textbbox((0, 0), prefix, font=font_body_bold)
                    prefix_w = bbox[2] - bbox[0]

                # Full text wrapping for content
                avail_first = max_w - (text_x + prefix_w - margin_x)
                words = content.split()
                first_line_words = []
                idx = 0
                while idx < len(words):
                    w_word = words[idx]
                    test = " ".join(first_line_words + [w_word]) if first_line_words else w_word
                    bbox = draw.textbbox((0, 0), test, font=font_body)
                    if (bbox[2] - bbox[0]) <= avail_first:
                        first_line_words.append(w_word)
                        idx += 1
                    else:
                        if not first_line_words:
                            first_line_words.append(w_word)
                            idx += 1
                        break

                if first_line_words:
                    draw.text((text_x + prefix_w, curr_y), " ".join(first_line_words), fill=body_color, font=font_body)
                    curr_y += int(font_body.size * 1.45)

                # Subsequent lines
                remaining_text = " ".join(words[idx:])
                if remaining_text:
                    sub_x = text_x + prefix_w if prefix and prefix[0].isdigit() else margin_x
                    sub_w = max_w - (sub_x - margin_x)
                    sub_lines = wrap_text_by_pixel(remaining_text, font_body, sub_w, draw)
                    for sl in sub_lines:
                        draw.text((sub_x, curr_y), sl, fill=body_color, font=font_body)
                        curr_y += int(font_body.size * 1.45)

                curr_y += int(font_body.size * 0.40)

        # Embedded Images (Single or Dual comparison side-by-side)
        raw_images = slide_data.get("images") or []
        if not raw_images and slide_data.get("image_asset"):
            raw_images = [slide_data["image_asset"]]
        elif not raw_images and slide_data.get("bg_image_path"):
            raw_images = [slide_data["bg_image_path"]]

        images = []
        for img_item in raw_images:
            p_img = Path(img_item)
            if p_img.is_file():
                images.append(p_img)
            else:
                ch_p = channel_data.get("path")
                if ch_p and (Path(ch_p) / img_item).is_file():
                    images.append(Path(ch_p) / img_item)
                elif Path(f"channels/{channel_data.get('slug', '')}/{img_item}").is_file():
                    images.append(Path(f"channels/{channel_data.get('slug', '')}/{img_item}"))
                else:
                    images.append(p_img)

        if images:
            img_y = max(curr_y + int(h * 0.03), int(h * 0.50))
            available_h = h - img_y - int(h * 0.09)
            if len(images) == 1:
                img_box = (margin_x, img_y, margin_x + max_w, img_y + available_h)
                self._draw_rounded_image(img, images[0], img_box, radius=18)
            else:  # Dual side-by-side
                gap = int(w * 0.025)
                each_w = (max_w - gap) // 2
                self._draw_rounded_image(img, images[0], (margin_x, img_y, margin_x + each_w, img_y + available_h), radius=18)
                self._draw_rounded_image(img, images[1], (margin_x + each_w + gap, img_y, margin_x + max_w, img_y + available_h), radius=18)

        # Footer dots
        foot_y = h - int(h * 0.045)
        r_text = f"{page_str}   {swipe_str}"
        font_foot = load_font_by_family("sans", size=int(w * 0.022), is_bold=False)
        bbox_r = draw.textbbox((0, 0), r_text, font=font_foot)
        draw.text((w - margin_x - (bbox_r[2] - bbox_r[0]), foot_y), r_text, fill=handle_color, font=font_foot)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(output_path, quality=95)
        return output_path

    def _render_split_editorial(
        self,
        output_path: Path,
        w: int,
        h: int,
        headline: str,
        body: str,
        page_str: str,
        swipe_str: str,
        channel_data: Dict[str, Any],
        slide_data: Dict[str, Any]
    ) -> Path:
        """Preset C: Corporate & GovTech Authority (Portal da Reforma Tributária style)."""
        vis_id = channel_data.get("visual_identity", {})
        pal = vis_id.get("palette", {})
        corporate_blue = hex_to_rgb(slide_data.get("card_background") or pal.get("card_background", "#0C2333"))
        accent_color = hex_to_rgb(slide_data.get("accent") or pal.get("accent", "#F59E0B"))

        img = Image.new("RGBA", (w, h), (10, 12, 16, 255))

        split_y = int(h * 0.44)
        top_img_path = slide_data.get("top_image") or slide_data.get("bg_image_path")
        if top_img_path and Path(top_img_path).is_file():
            self._draw_rounded_image(img, top_img_path, (0, 0, w, split_y), radius=0)

        # Bottom solid corporate container
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, split_y, w, h], fill=(*corporate_blue, 255))

        # Circular author cutout overlapping split line
        author_avatar = slide_data.get("author_avatar") or vis_id.get("author", {}).get("avatar_path")
        av_size = int(w * 0.22)
        av_x = w - int(w * 0.08) - av_size
        av_y = split_y - int(av_size * 0.48)
        self._draw_circular_avatar(
            img, author_avatar, av_x, av_y, av_size,
            fallback_initials=channel_data.get("name", "RT"),
            primary_rgb=accent_color,
            border_color=corporate_blue
        )

        margin_x = int(w * 0.08)
        curr_y = split_y + int(h * 0.05)

        # Brand Badge & Opinion Label
        badge_text = slide_data.get("badge_text") or f"{channel_data.get('name', 'PORTAL').upper()} | OPINIÃO"
        font_badge = load_font_by_family("sans", size=int(w * 0.024), is_bold=True)
        draw.text((margin_x, curr_y), badge_text, fill=(*accent_color, 255), font=font_badge)
        curr_y += int(font_badge.size * 1.8)

        # Headline with Square Bullets (■)
        font_head = load_font_by_family("sans", size=int(w * 0.046), is_bold=True)
        lines = headline.split("\n") if "\n" in headline else wrap_text_by_pixel(headline, font_head, int(w * 0.84), draw)

        bullet_s = int(w * 0.026)
        for line in lines:
            draw.rectangle([margin_x, curr_y + 8, margin_x + bullet_s, curr_y + 8 + bullet_s], fill=(*accent_color, 255))
            draw.text((margin_x + bullet_s + 14, curr_y), line.strip(), fill=(255, 255, 255, 255), font=font_head)
            curr_y += int(font_head.size * 1.35)

        curr_y += int(h * 0.02)

        # Body text
        if body:
            font_body = load_font_by_family("sans", size=int(w * 0.030), is_bold=False)
            b_lines = wrap_text_by_pixel(body, font_body, int(w * 0.84), draw)
            for bline in b_lines:
                draw.text((margin_x, curr_y), bline, fill=(225, 235, 245, 255), font=font_body)
                curr_y += int(font_body.size * 1.40)

        # Watermark in bottom right
        watermark = slide_data.get("watermark_text") or vis_id.get("elements", {}).get("watermark_text", "RT")
        foot_y = h - int(h * 0.055)
        font_wm = load_font_by_family("sans", size=int(w * 0.036), is_bold=True)
        draw.text((w - margin_x - int(w * 0.08), foot_y - 6), watermark, fill=(255, 255, 255, 230), font=font_wm)

        # Footer handle
        font_foot = load_font_by_family("sans", size=int(w * 0.022), is_bold=False)
        r_text = f"{page_str}   {swipe_str}"
        draw.text((margin_x, foot_y), r_text, fill=(180, 200, 220, 200), font=font_foot)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(output_path, quality=95)
        return output_path

    def _render_classic_card(
        self,
        bg_image_path: Optional[Path],
        output_path: Path,
        w: int,
        h: int,
        channel_slug: str,
        headline: str,
        body: str,
        badge_text: Optional[str],
        page_str: str,
        swipe_str: str,
        gradient_start_ratio: float,
        aspect_ratio: str,
        enable_text_card: bool,
        card_bg_alpha: int,
        stroke_width: Optional[int],
    ) -> Path:
        """Preset D: Classic Archival Contrast Card (Rule 08 Dossiê Histórico style)."""
        channel = self.channel_manager.get_channel(channel_slug) or self.channel_manager.get_active_channel()
        branding = channel.get("branding", {})
        colors = branding.get("theme_colors", {})
        typography = branding.get("typography", {})

        primary_rgb = hex_to_rgb(colors.get("primary", "#D4AF37"))
        handle = branding.get("handle", "@canal")
        badge = badge_text or branding.get("badge_text", channel.get("name", "OMNIPRESS"))

        bold_font_path = typography.get("bold_font")
        reg_font_path = typography.get("regular_font")

        if bg_image_path and Path(bg_image_path).is_file():
            with Image.open(bg_image_path) as raw_img:
                if raw_img.mode in ("RGBA", "LA") or (raw_img.mode == "P" and "transparency" in raw_img.info):
                    rgba = raw_img.convert("RGBA")
                    bg_card = Image.new("RGBA", rgba.size, (10, 12, 16, 255))
                    img = Image.alpha_composite(bg_card, rgba)
                else:
                    img = raw_img.convert("RGBA")
        else:
            img = Image.new("RGBA", (w, h), (10, 12, 16, 255))

        # Crop to target aspect ratio if needed
        ratio_map = {"3:4": 3 / 4, "4:5": 4 / 5, "1:1": 1.0, "9:16": 9 / 16, "16:9": 16 / 9}
        target_ratio = ratio_map.get(aspect_ratio, 3 / 4)
        curr_ratio = img.width / img.height
        if curr_ratio < target_ratio - 0.05:
            target_h = int(img.width / target_ratio)
            top = (img.height - target_h) // 2
            img = img.crop((0, top, img.width, top + target_h))
        elif curr_ratio > target_ratio + 0.05:
            target_w = int(img.height * target_ratio)
            left = (img.width - target_w) // 2
            img = img.crop((left, 0, left + target_w, img.height))
        w, h = img.size

        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        font_head = load_safe_font(bold_font_path, size=max(20, int(w * 0.046)), is_bold=True)
        font_body = load_safe_font(reg_font_path, size=max(16, int(w * 0.034)), is_bold=False)
        font_foot = load_safe_font(bold_font_path, size=max(14, int(w * 0.024)), is_bold=True)

        margin_x = int(w * 0.065)
        max_text_w = w - (margin_x * 2)

        head_lines = wrap_text_by_pixel(headline, font_head, max_text_w, draw)
        body_lines = wrap_text_by_pixel(body, font_body, max_text_w, draw) if body else []

        line_h_head = int(getattr(font_head, "size", 40) * 1.25)
        line_h_body = int(getattr(font_body, "size", 30) * 1.35)

        total_h = len(head_lines) * line_h_head + 14 + len(body_lines) * line_h_body
        start_y = max(int(h * 0.08), h - total_h - int(h * 0.11))

        # Bottom gradient
        grad_start = min(int(h * gradient_start_ratio), max(0, start_y - int(h * 0.06)))
        for y in range(grad_start, h):
            progress = (y - grad_start) / max(1, (h - grad_start))
            alpha = int(252 * (progress ** 0.85))
            draw.line([(0, y), (w, y)], fill=(8, 10, 14, min(252, alpha)))

        # Top vignette
        for y in range(int(h * 0.13)):
            alpha = int(180 * (1 - (y / (h * 0.13))))
            draw.line([(0, y), (w, y)], fill=(8, 10, 14, min(180, alpha)))

        # Top Badge
        badge_content = f"• {badge.upper()} | {handle.upper()} •"
        bx, by = int(w * 0.06), int(h * 0.045)
        max_badge_w = w - (bx * 2) - 28
        badge_size = max(14, int(w * 0.024))
        font_badge = load_safe_font(bold_font_path, size=badge_size, is_bold=True)
        bbox_b = draw.textbbox((0, 0), badge_content, font=font_badge)
        bw, bh = bbox_b[2] - bbox_b[0], bbox_b[3] - bbox_b[1]
        while bw > max_badge_w and badge_size > 10:
            badge_size -= 1
            font_badge = load_safe_font(bold_font_path, size=badge_size, is_bold=True)
            bbox_b = draw.textbbox((0, 0), badge_content, font=font_badge)
            bw, bh = bbox_b[2] - bbox_b[0], bbox_b[3] - bbox_b[1]

        draw.rounded_rectangle(
            [bx - 14, by - 8, bx + bw + 14, by + bh + 8],
            radius=8,
            fill=(*primary_rgb, 235)
        )
        draw.text((bx, by), badge_content, fill=(10, 12, 16, 255), font=font_badge)

        # Protective Opaque/Translucent Text Backdrop Card (Rule 08)
        if enable_text_card and (head_lines or body_lines):
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

        # Text with Safety Stroke
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

        # Footer
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

    # -------------------------------------------------------------------------
    # Public Unified API
    # -------------------------------------------------------------------------

    def render_slide(
        self,
        bg_image_path: Optional[Path],
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
        preset: Optional[str] = None,
        slide_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Path:
        """
        Renders a single branded carousel slide, automatically dispatching to the configured visual preset.
        Presets: 'tweet_card', 'minimal_dark', 'split_editorial', 'classic_card'.
        """
        channel = self.channel_manager.get_channel(channel_slug) or self.channel_manager.get_active_channel()
        data = slide_data or {}
        if bg_image_path:
            data.setdefault("bg_image_path", str(bg_image_path))

        # Resolve preset
        chosen_preset = preset or data.get("layout") or channel.get("visual_identity", {}).get("default_preset", "classic_card")

        dim_map = {
            "3:4": (1080, 1440),
            "4:5": (1080, 1350),
            "1:1": (1080, 1080),
            "9:16": (1080, 1920),
            "16:9": (1920, 1080),
        }
        w, h = dim_map.get(aspect_ratio, (1080, 1440))

        if chosen_preset == "minimal_dark":
            return self._render_minimal_dark(
                output_path=output_path,
                w=w,
                h=h,
                headline=headline,
                body=body,
                page_str=page_str,
                swipe_str=swipe_str,
                channel_data=channel,
                slide_data=data
            )
        elif chosen_preset == "tweet_card":
            return self._render_tweet_card(
                output_path=output_path,
                w=w,
                h=h,
                headline=headline,
                body=body,
                page_str=page_str,
                swipe_str=swipe_str,
                channel_data=channel,
                slide_data=data
            )
        elif chosen_preset == "split_editorial":
            return self._render_split_editorial(
                output_path=output_path,
                w=w,
                h=h,
                headline=headline,
                body=body,
                page_str=page_str,
                swipe_str=swipe_str,
                channel_data=channel,
                slide_data=data
            )
        else:
            # Fallback to classic_card (Rule 08)
            return self._render_classic_card(
                bg_image_path=bg_image_path,
                output_path=output_path,
                w=w,
                h=h,
                channel_slug=channel_slug,
                headline=headline,
                body=body,
                badge_text=badge_text,
                page_str=page_str,
                swipe_str=swipe_str,
                gradient_start_ratio=gradient_start_ratio,
                aspect_ratio=aspect_ratio,
                enable_text_card=enable_text_card,
                card_bg_alpha=card_bg_alpha,
                stroke_width=stroke_width,
            )

    def build_carousel(
        self,
        channel_slug: str,
        post_slug: str,
        slides_data: List[Dict[str, Any]],
        aspect_ratio: str = "3:4",
        default_preset: Optional[str] = None
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

            swipe_text = slide.get("swipe_str") or ("Deslize →" if idx < total_pages else "Salve & Siga")
            bg_path_str = slide.get("bg_image_path")
            bg_path = Path(bg_path_str) if bg_path_str else None

            slide_layout = slide.get("layout") or default_preset

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
                preset=slide_layout,
                slide_data=slide,
            )
            generated_paths.append(out_file)

        return generated_paths
