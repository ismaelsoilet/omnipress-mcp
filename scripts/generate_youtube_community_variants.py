"""
Renderizador de variantes de alta conversão para o YouTube Community Card / Thumbnail
Baseado estritamente na Regra 15 (Tipografia Titânica, Chiaroscuro e Anti-Microtexto)
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

W, H = 1920, 1080
ANTON = "channels/dossie-historico/recursos_globais/fontes/Anton-Regular.ttf"
MONTSERRAT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def render_community_card(bg_path: Path, out_path: Path, headline_l1: str, headline_l2: str, highlight_word: str, badge_text: str, tagline_text: str):
    # 1. Base Image with cover fit
    with Image.open(bg_path) as raw:
        base = raw.convert("RGB")
    
    # Scale to cover 1920x1080
    target_ratio = W / H
    w, h = base.size
    ratio = w / h
    if ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        base = base.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = int((h - new_h) * 0.25)
        base = base.crop((0, top, w, top + new_h))
    
    canvas = base.resize((W, H), Image.Resampling.LANCZOS)
    # Enhance contrast and slight desaturation for dramatic historical noir look
    canvas = ImageEnhance.Contrast(canvas).enhance(1.22)

    # 2. Chiaroscuro Gradient Shield (Left 55% dark isolation)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    limit = int(W * 0.60)
    for x in range(limit):
        progress = x / max(1, limit - 1)
        # Deep opaque black on the left, curving out smoothly to transparent
        alpha = int(248 * ((1.0 - progress) ** 0.85))
        ov_draw.line([(x, 0), (x, H)], fill=(4, 6, 10, alpha))
    
    # Cinematic letterbox shade top/bottom
    for y in range(80):
        a = int(180 * (1.0 - y / 80.0))
        ov_draw.line([(0, y), (W, y)], fill=(4, 6, 10, a))
    for y in range(H - 80, H):
        a = int(180 * ((y - (H - 80)) / 80.0))
        ov_draw.line([(0, y), (W, y)], fill=(4, 6, 10, a))

    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(canvas)

    # 3. Typography (Rule 15 Titanic Scale)
    margin_x = 90
    stroke_w = 14
    stroke_rgb = (0, 0, 0, 255)
    shadow_rgb = (0, 0, 0, 240)
    shadow_offset = (0, 10)

    # Top Authority Badge: Montserrat ExtraBold (56px)
    if badge_text:
        font_badge = ImageFont.truetype(MONTSERRAT, 52)
        bbox_b = draw.textbbox((0, 0), badge_text.upper(), font=font_badge)
        bw = bbox_b[2] - bbox_b[0] + 44
        bh = bbox_b[3] - bbox_b[1] + 20
        by = 85
        draw.rounded_rectangle([margin_x, by, margin_x + bw, by + bh], radius=12, fill=(212, 175, 55, 245))
        draw.text((margin_x + 22, by + 9), badge_text.upper(), fill=(10, 12, 16, 255), font=font_badge)

    # Headline Line 1: Anton (180px)
    font_h1 = ImageFont.truetype(ANTON, 180)
    h1_y = 210

    # Draw deep drop shadow
    draw.text((margin_x + shadow_offset[0], h1_y + shadow_offset[1]), headline_l1, font=font_h1, fill=shadow_rgb, stroke_width=stroke_w + 4, stroke_fill=shadow_rgb)
    # Draw stroke & fill
    draw.text((margin_x, h1_y), headline_l1, font=font_h1, fill=(255, 255, 255, 255), stroke_width=stroke_w, stroke_fill=stroke_rgb)

    # Headline Line 2: Anton (195px)
    font_h2 = ImageFont.truetype(ANTON, 195)
    h2_y = h1_y + int(180 * 0.98)

    # Highlight word logic: if highlight_word in line 2, color it in Alert Gold (#FFE500)
    draw.text((margin_x + shadow_offset[0], h2_y + shadow_offset[1]), headline_l2, font=font_h2, fill=shadow_rgb, stroke_width=stroke_w + 4, stroke_fill=shadow_rgb)
    draw.text((margin_x, h2_y), headline_l2, font=font_h2, fill=(255, 229, 0, 255), stroke_width=stroke_w, stroke_fill=stroke_rgb)

    # Tagline / Subtitle: Montserrat ExtraBold (52px)
    if tagline_text:
        tag_y = h2_y + int(195 * 1.05)
        font_tag = ImageFont.truetype(MONTSERRAT, 52)
        draw.text((margin_x + 4, tag_y + 4), tagline_text.upper(), font=font_tag, fill=(0, 0, 0, 220), stroke_width=6, stroke_fill=(0, 0, 0, 220))
        draw.text((margin_x, tag_y), tagline_text.upper(), font=font_tag, fill=(212, 175, 55, 255), stroke_width=4, stroke_fill=(10, 12, 16, 255))

    # Save master image
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out_path, "JPEG", quality=95)
    print(f"Generated: {out_path.name}")

    # Generate 120px mobile preview for Squint Test (Rule 15 Law 8)
    preview_120 = canvas.resize((120, int(120 / target_ratio)), Image.Resampling.LANCZOS)
    preview_120_p = out_path.parent / f"preview_120px_{out_path.stem}.jpg"
    preview_120.convert("RGB").save(preview_120_p, "JPEG", quality=85)

    preview_320 = canvas.resize((320, int(320 / target_ratio)), Image.Resampling.LANCZOS)
    preview_320_p = out_path.parent / f"preview_320px_{out_path.stem}.jpg"
    preview_320.convert("RGB").save(preview_320_p, "JPEG", quality=85)


raw_dir = Path("channels/dossie-historico/episodios/ep04_operacao_mincemeat/carrossel/midias/raw")
doc_dir = Path("channels/dossie-historico/episodios/ep04_operacao_mincemeat/documentario/midias")
out_dir = Path("channels/dossie-historico/episodios/ep04_operacao_mincemeat/posts/community_card_variants")

# Variant 1: Maleta Oficial / Desclassificada
render_community_card(
    bg_path=raw_dir / "mincemeat_capa_maleta_1791739182879.jpg",
    out_path=out_dir / "variant_1_maleta.jpg",
    headline_l1="O CORPO QUE",
    headline_l2="ENGANOU HITLER",
    highlight_word="HITLER",
    badge_text="CASO REAL • 1943",
    tagline_text="OPERAÇÃO MINCEMEAT"
)

# Variant 2: Submarino Seraph em Alta Tensão
render_community_card(
    bg_path=raw_dir / "mincemeat_submarino_seraph_1791739294740.jpg",
    out_path=out_dir / "variant_2_submarino.jpg",
    headline_l1="O CORPO QUE",
    headline_l2="ENGANOU HITLER",
    highlight_word="HITLER",
    badge_text="ARQUIVO DESCLASSIFICADO",
    tagline_text="OPERAÇÃO MINCEMEAT"
)

# Variant 3: Corrente de Aço e Custódia de Prova
render_community_card(
    bg_path=doc_dir / "4_corrente_aco_maleta_pulso.jpg",
    out_path=out_dir / "variant_3_corrente_aco.jpg",
    headline_l1="ENGANOU",
    headline_l2="HITLER!",
    highlight_word="HITLER!",
    badge_text="CASO REAL • 1943",
    tagline_text="O HOMEM QUE NUNCA EXISTIU"
)
