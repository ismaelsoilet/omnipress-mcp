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


if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__, "-v"]))

