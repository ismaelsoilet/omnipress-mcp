"""Unit tests for OmniPress Agnostic Carousel Builder."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pytest

from src.engine.carousel_builder import CarouselBuilder, hex_to_rgb, wrap_text_by_pixel
from src.core.channel_manager import ChannelManager


def test_hex_to_rgb():
    assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
    assert hex_to_rgb("#000000") == (0, 0, 0)
    assert hex_to_rgb("#D4AF37") == (212, 175, 55)
    # Test 3-char shorthand
    assert hex_to_rgb("#FFF") == (255, 255, 255)
    # Test invalid hex fallback (gold default)
    assert hex_to_rgb("invalid") == (212, 175, 55)


def test_wrap_text_by_pixel():
    img = Image.new("RGBA", (1000, 1000), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    sample = "Esta é uma frase de teste longa o suficiente para ser quebrada em multiplas linhas no carrossel"
    lines = wrap_text_by_pixel(sample, font, max_width=150, draw=draw)
    assert len(lines) > 1
    assert " ".join(lines) == sample


def test_render_slide_and_build_carousel(tmp_path: Path):
    # Setup temporary background image
    bg_img_path = tmp_path / "bg.jpg"
    bg = Image.new("RGB", (1080, 1440), (20, 25, 35))
    bg.save(bg_img_path)

    # Initialize ChannelManager and create a test channel
    cm = ChannelManager(root_dir=tmp_path)
    cm.create_channel(
        slug="canal-teste",
        name="Canal de Testes",
        primary_color="#D4AF37",
        handle="@canal.teste"
    )

    builder = CarouselBuilder(channel_manager=cm)

    # Test single slide rendering
    out_slide = tmp_path / "slide_01.jpg"
    res_path = builder.render_slide(
        bg_image_path=bg_img_path,
        output_path=out_slide,
        channel_slug="canal-teste",
        headline="Título de Alto Impacto",
        body="Texto explicativo detalhado cumprindo a Regra 08 de contraste e backdrop protetor.",
        badge_text="DOSSIÊ TESTE",
        page_str="01/05",
        swipe_str="Deslize →",
        aspect_ratio="3:4",
        enable_text_card=True,
    )

    assert res_path.exists()
    rendered_img = Image.open(res_path)
    assert rendered_img.size == (1080, 1440)  # 3:4 aspect ratio

    # Test full multi-slide carousel building
    slides_data = [
        {"bg_image_path": str(bg_img_path), "headline": "Slide 1", "body": "Conteúdo 1"},
        {"bg_image_path": str(bg_img_path), "headline": "Slide 2", "body": "Conteúdo 2"},
    ]
    carousel_files = builder.build_carousel(
        channel_slug="canal-teste",
        post_slug="post-teste-01",
        slides_data=slides_data,
        aspect_ratio="3:4"
    )

    assert len(carousel_files) == 2
    for cf in carousel_files:
        assert cf.exists()
        assert "post-teste-01" in str(cf)


def test_render_tweet_card_preset(tmp_path: Path):
    cm = ChannelManager(root_dir=tmp_path)
    cm.create_channel(
        slug="thiago-mkt",
        name="Thiago Ramos",
        primary_color="#1D9BF0",
        handle="@thiagoramos.mkt",
        archetype="personal_brand"
    )
    builder = CarouselBuilder(channel_manager=cm)

    out_file = tmp_path / "slide_tweet.jpg"
    res = builder.render_slide(
        bg_image_path=None,
        output_path=out_file,
        channel_slug="thiago-mkt",
        headline="Não fazer campanha foi a melhor campanha de Tarcísio!",
        body="Entenda por que é preciso construir uma base muito antes da eleição.",
        preset="tweet_card",
        aspect_ratio="4:5",
        slide_data={
            "author": {
                "name": "Thiago Ramos",
                "handle": "@thiagoramos.mkt",
                "verified": True
            }
        }
    )
    assert res.exists()
    img = Image.open(res)
    assert img.size == (1080, 1350)  # 4:5 aspect ratio


def test_render_minimal_dark_preset(tmp_path: Path):
    cm = ChannelManager(root_dir=tmp_path)
    cm.create_channel(
        slug="rhaj-dark",
        name="Rhaj Teixeira",
        primary_color="#FFFFFF",
        handle="@rhajtxeira",
        archetype="personal_brand"
    )
    builder = CarouselBuilder(channel_manager=cm)

    out_file = tmp_path / "slide_minimal.jpg"
    res = builder.render_slide(
        bg_image_path=None,
        output_path=out_file,
        channel_slug="rhaj-dark",
        headline="Pesquise por boring history for sleep.",
        body="Encontre o que está funcionando, com disparidade de inscritos e visualizações.",
        preset="minimal_dark",
        aspect_ratio="4:5",
        slide_data={
            "step_number": "Passo 1.",
            "ui_mockup": {
                "type": "search_bar",
                "query": "boring history for sleep"
            }
        }
    )
    assert res.exists()
    img = Image.open(res)
    assert img.size == (1080, 1350)  # 4:5 aspect ratio


def test_render_split_editorial_preset(tmp_path: Path):
    cm = ChannelManager(root_dir=tmp_path)
    cm.create_channel(
        slug="portal-tributario",
        name="Portal da Reforma Tributária",
        primary_color="#F59E0B",
        handle="@portaldareformatributaria",
        archetype="media_channel"
    )
    builder = CarouselBuilder(channel_manager=cm)

    # Fake top photo
    top_img = tmp_path / "brasilia.jpg"
    Image.new("RGB", (1080, 600), (40, 60, 90)).save(top_img)

    out_file = tmp_path / "slide_split.jpg"
    res = builder.render_slide(
        bg_image_path=None,
        output_path=out_file,
        channel_slug="portal-tributario",
        headline="CBS e anterioridade\nnonagesimal.\nO Executivo dormiu\nno ponto?",
        body="Uma análise detalhada sobre os prazos de vigência da nova tributação sobre o consumo.",
        preset="split_editorial",
        aspect_ratio="4:5",
        slide_data={
            "top_image": str(top_img),
            "badge_text": "PAULO ANDRADE | OPINIÃO",
            "bullet_style": "square",
            "watermark_text": "RT"
        }
    )
    assert res.exists()
    img = Image.open(res)
    assert img.size == (1080, 1350)  # 4:5 aspect ratio


def test_parse_semantic_line():
    pal = {
        "danger": "#EF4444",
        "success": "#10B981",
        "warning": "#F59E0B",
        "accent": "#3B82F6",
    }
    custom_tags = {
        "DICA:": "#8B5CF6",
        "ATENÇÃO:": "#EC4899",
    }

    # 1. Test standard tags
    dot, prefix, p_color, content = CarouselBuilder._parse_semantic_line(
        "MITO: O IBS entra em vigor imediatamente",
        pal=pal,
        is_dark=True,
        custom_tags=custom_tags,
    )
    assert prefix == "MITO: "
    assert p_color == (239, 68, 68, 255)
    assert content == "O IBS entra em vigor imediatamente"

    dot, prefix, p_color, content = CarouselBuilder._parse_semantic_line(
        "VERDADE: A transição completa é até 2033",
        pal=pal,
        is_dark=True,
        custom_tags=custom_tags,
    )
    assert prefix == "VERDADE: "
    assert p_color == (16, 185, 129, 255)
    assert content == "A transição completa é até 2033"

    # 2. Test channel-custom tag
    dot, prefix, p_color, content = CarouselBuilder._parse_semantic_line(
        "DICA: Prepare seu ERP com antecedência",
        pal=pal,
        is_dark=False,
        custom_tags=custom_tags,
    )
    assert prefix == "DICA: "
    assert p_color == (139, 92, 246, 255)
    assert content == "Prepare seu ERP com antecedência"

    # 3. Test numbered list
    dot, prefix, p_color, content = CarouselBuilder._parse_semantic_line(
        "1. Realize o saneamento cadastral de produtos",
        pal=pal,
        is_dark=True,
        custom_tags=custom_tags,
    )
    assert prefix == "1. "
    assert p_color == (59, 130, 246, 255)
    assert content == "Realize o saneamento cadastral de produtos"

    # 4. Test bullet list
    dot, prefix, p_color, content = CarouselBuilder._parse_semantic_line(
        "• Alíquota padrão estimada em 27%",
        pal=pal,
        is_dark=True,
        custom_tags=custom_tags,
    )
    assert dot == (59, 130, 246, 255)
    assert prefix == ""
    assert content == "Alíquota padrão estimada em 27%"


def test_resolve_param_hierarchy():
    builder = CarouselBuilder()

    channel_data = {
        "branding": {"legacy_param": "from_branding"},
        "visual_identity": {
            "layout_parameters": {
                "margin_ratio": 0.08,
                "border_radius": 24,
            },
            "presets": {
                "tweet_card": {
                    "border_radius": 30,
                }
            }
        }
    }

    # 1. Slide-level override beats everything
    slide = {"margin_ratio": 0.12}
    res = builder._resolve_param("margin_ratio", slide_data=slide, channel_data=channel_data, preset_name="tweet_card", default=0.05)
    assert res == 0.12

    # 2. Preset-specific override in channel beats channel-wide layout_parameters
    res = builder._resolve_param("border_radius", slide_data={}, channel_data=channel_data, preset_name="tweet_card", default=10)
    assert res == 30

    # 3. Channel-wide layout_parameters beats default
    res = builder._resolve_param("margin_ratio", slide_data={}, channel_data=channel_data, preset_name="minimal_dark", default=0.05)
    assert res == 0.08

    # 4. Legacy branding parameter resolution
    res = builder._resolve_param("legacy_param", slide_data={}, channel_data=channel_data, preset_name="tweet_card", default="fallback")
    assert res == "from_branding"

    # 5. Fallback to default when not specified anywhere
    res = builder._resolve_param("non_existent", slide_data={}, channel_data=channel_data, preset_name="tweet_card", default="safe_default")
    assert res == "safe_default"


def test_parse_semantic_line_custom_categories():
    pal = {"primary": "#3B82F6", "accent": "#3B82F6", "danger": "#EF4444", "success": "#10B981", "warning": "#F59E0B"}
    custom_categories = {
        "danger": ["ANTIPATTERN", "DEPRECATED", "FALHA"],
        "success": ["PADRÃO", "BOA PRÁTICA"],
        "warning": ["TRADE-OFF"]
    }

    # Channel-specific danger keyword
    dot, prefix, p_color, content = CarouselBuilder._parse_semantic_line(
        "ANTIPATTERN: Injeção de dependência via singleton global",
        pal=pal,
        is_dark=True,
        semantic_categories=custom_categories,
    )
    assert prefix == "ANTIPATTERN: "
    assert p_color == (239, 68, 68, 255)
    assert content == "Injeção de dependência via singleton global"

    # Channel-specific success keyword
    dot, prefix, p_color, content = CarouselBuilder._parse_semantic_line(
        "PADRÃO: Usar inversão de controle com containers leves",
        pal=pal,
        is_dark=True,
        semantic_categories=custom_categories,
    )
    assert prefix == "PADRÃO: "
    assert p_color == (16, 185, 129, 255)

    # Channel-specific warning keyword
    dot, prefix, p_color, content = CarouselBuilder._parse_semantic_line(
        "TRADE-OFF: Maior desacoplamento versus complexidade inicial",
        pal=pal,
        is_dark=True,
        semantic_categories=custom_categories,
    )
    assert prefix == "TRADE-OFF: "
    assert p_color == (245, 158, 11, 255)


def test_render_slide_with_channel_layout_parameters(tmp_path: Path):
    cm = ChannelManager(root_dir=tmp_path)
    cm.create_channel(
        slug="dev-brand",
        name="Developer Brand",
        primary_color="#0A66C2",
        handle="@devbrand"
    )

    # Update channel with custom layout_parameters
    ch_file = tmp_path / "channels" / "dev-brand" / "channel.json"
    import json
    data = json.loads(ch_file.read_text(encoding="utf-8"))
    data["visual_identity"] = {
        "default_preset": "tweet_card",
        "layout_parameters": {
            "margin_ratio": 0.10,
            "headline_scale": 0.060,
            "body_scale": 0.040,
            "border_radius": 24,
            "show_verified_badge": True
        },
        "semantic_tags": {
            "ARQUITETURA": "#0A66C2"
        }
    }
    ch_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    builder = CarouselBuilder(channel_manager=cm)
    out_slide = tmp_path / "slide_param.jpg"
    res = builder.render_slide(
        bg_image_path=None,
        output_path=out_slide,
        channel_slug="dev-brand",
        headline="Arquitetura de Alta Escalabilidade",
        body="ARQUITETURA: Serviços isolados e desacoplados.",
        aspect_ratio="3:4"
    )

    assert res.exists()
    img = Image.open(res)
    assert img.size == (1080, 1440)


if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__, "-v"]))

