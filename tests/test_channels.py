"""Tests for OmniPress Multi-Channel Agnostic Architecture."""

import json
from pathlib import Path
from PIL import Image

from src.core.channel_manager import ChannelManager, slugify_channel
from src.engine.carousel_builder import CarouselBuilder, hex_to_rgb
from src.adapters.markdown_adapter import MarkdownArchiveAdapter
from src.server import (
    MCP_TOOL_ANNOTATIONS,
    omnipress_list_channels,
    omnipress_get_channel,
    omnipress_create_channel,
    omnipress_build_carousel,
)


def test_slugify_channel():
    assert slugify_channel("Meu Canal Novo") == "meu-canal-novo"
    assert slugify_channel("@tech_daily.canal") == "tech-dailycanal"
    assert slugify_channel("GovTech Brasil") == "govtech-brasil"


def test_channel_manager_discovery():
    cm = ChannelManager()
    # Channels excluding templates should not include _template
    channels = cm.list_channels(include_templates=False)
    slugs = [c["slug"] for c in channels]
    assert "_template" not in slugs

    # With templates included, template-channel must be present
    channels_with_tpl = cm.list_channels(include_templates=True)
    slugs_with_tpl = [c["slug"] for c in channels_with_tpl]
    assert "template-channel" in slugs_with_tpl


def test_channel_manager_scaffolding_and_get(tmp_path: Path):
    cm = ChannelManager(root_dir=tmp_path)
    res = cm.create_channel(
        slug="tech-trends",
        name="Tech Trends Hub",
        handle="@techtrends.br",
        category="technology",
        description="Novidades de IA e desenvolvimento.",
        primary_color="#3B82F6",
        buffer_channel_id="buffer-test-123",
        default_hashtags=["#tech", "#ia", "#coding"]
    )

    channel_dir = tmp_path / "channels" / "tech-trends"
    assert channel_dir.exists()
    assert (channel_dir / "articles").exists()
    assert (channel_dir / "media" / "carousels").exists()
    assert (channel_dir / "media" / "stories").exists()
    assert (channel_dir / "media" / "highlights").exists()
    assert (channel_dir / "media" / "raw").exists()
    assert (channel_dir / "scripts").exists()

    config_path = channel_dir / "channel.json"
    assert config_path.exists()
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["slug"] == "tech-trends"
    assert data["name"] == "Tech Trends Hub"
    assert data["branding"]["handle"] == "@techtrends.br"
    assert data["branding"]["theme_colors"]["primary"] == "#3B82F6"
    assert data["social"]["instagram"]["buffer_channel_id"] == "buffer-test-123"
    assert "#tech" in data["social"]["instagram"]["default_hashtags"]

    # Test get_channel on created channel
    fetched = cm.get_channel("tech-trends")
    assert fetched is not None
    assert fetched["slug"] == "tech-trends"
    assert fetched["branding"]["handle"] == "@techtrends.br"

    # Inexistent channel
    assert cm.get_channel("canal-inexistente") is None


def test_carousel_builder_helpers():
    assert hex_to_rgb("#D4AF37") == (212, 175, 55)
    assert hex_to_rgb("#3B82F6") == (59, 130, 246)
    assert hex_to_rgb("#FFF") == (255, 255, 255)
    assert hex_to_rgb("invalid") == (212, 175, 55)


def test_carousel_builder_rendering(tmp_path: Path):
    cm = ChannelManager(root_dir=tmp_path)
    cm.create_channel(
        slug="test-brand",
        name="Test Brand",
        handle="@testbrand",
        primary_color="#10B981"
    )
    builder = CarouselBuilder(cm)

    # Create dummy background image (1080x1440 3:4)
    dummy_bg = tmp_path / "dummy_bg.jpg"
    img = Image.new("RGB", (1080, 1440), color=(30, 40, 50))
    img.save(dummy_bg, format="JPEG")

    out_slide = tmp_path / "out_slide.jpg"
    rendered = builder.render_slide(
        bg_image_path=dummy_bg,
        output_path=out_slide,
        channel_slug="test-brand",
        headline="TESTE DE HEADLINE DO CANAL",
        body="Este é um teste de renderização pixel-perfect com o novo construtor de carrosséis.",
        page_str="01/05",
        swipe_str="Deslize →",
        aspect_ratio="3:4"
    )

    assert rendered.exists()
    with Image.open(rendered) as out_img:
        assert out_img.size[0] == 1080
        assert out_img.size[1] == 1440


def test_markdown_channel_isolation(tmp_path: Path):
    # Set explicit base_dir in tmp_path
    adapter = MarkdownArchiveAdapter(base_dir=str(tmp_path / "articles"))
    res = adapter.save_article(
        title="Artigo Isolado do Canal",
        content_markdown="Conteúdo técnico seguro.",
        category="tecnologia",
        tags=["python", "mcp"],
    )

    assert res["success"] is True
    file_path = Path(res["filepath"])
    assert file_path.exists()
    assert str(tmp_path) in str(file_path)


def test_mcp_channel_tools(tmp_path: Path):
    # Test annotations
    for tool_name in ["omnipress_list_channels", "omnipress_get_channel", "omnipress_create_channel", "omnipress_build_carousel"]:
        assert tool_name in MCP_TOOL_ANNOTATIONS, f"Missing annotation for {tool_name}"
        annot = MCP_TOOL_ANNOTATIONS[tool_name]
        for k in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"):
            assert isinstance(annot.get(k), bool)

    # Test list_channels returns valid output
    list_output = omnipress_list_channels(include_templates=True)
    assert "template-channel" in list_output or "OmniPress Channels" in list_output

    # Test create_channel MCP tool
    created_msg = omnipress_create_channel(
        slug="mcp-test-channel",
        name="MCP Test Channel",
        handle="@mcptest",
        category="testing",
        primary_color="#8B5CF6"
    )
    assert "mcp-test-channel" in created_msg

    # Test get_channel for created channel
    get_output = omnipress_get_channel("mcp-test-channel")
    parsed = json.loads(get_output)
    assert parsed["slug"] == "mcp-test-channel"
    assert parsed["branding"]["handle"] == "@mcptest"
    assert parsed["branding"]["theme_colors"]["primary"] == "#8B5CF6"

    # Clean up test channel created by tool
    import shutil
    target_clean = Path(__file__).resolve().parent.parent / "channels" / "mcp-test-channel"
    if target_clean.exists():
        shutil.rmtree(target_clean)


def test_dossie_historico_channel_config():
    cm = ChannelManager()
    dossie = cm.get_channel("dossie-historico")
    assert dossie is not None
    assert dossie["slug"] == "dossie-historico"
    assert "instagram" in dossie["social"]
    assert "youtube" in dossie["social"]
    assert "tiktok" in dossie["social"]
    assert dossie["social"]["tiktok"]["buffer_channel_id"] == "6acd5268778b240e2fed378b"
    assert dossie["social"]["instagram"]["buffer_channel_id"] == "6acaa9ad6a5c39ccb67710a2"
    assert dossie["social"]["youtube"]["buffer_channel_id"] == "6acd4b28778b240e2feca987"


if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
