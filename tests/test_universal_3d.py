"""Tests for Universal 3D Engine and Blender Headless integration in OmniPress."""

import json
from pathlib import Path
import pytest
from PIL import Image

from src.engine.universal_3d import Universal3DEngine, BlenderRenderError
from src.utils.runtime_checker import get_runtime_capabilities, format_doctor_report
from src.server import omnipress_render_3d, MCP_TOOL_ANNOTATIONS


@pytest.fixture
def test_texture_path(tmp_path: Path) -> Path:
    """Creates a temporary sample 1080x1920 test texture."""
    img_path = tmp_path / "sample_texture.png"
    img = Image.new("RGBA", (1080, 1920), color=(30, 40, 70, 255))
    img.save(img_path)
    return img_path


def test_blender_binary_discovery():
    """AC-01: Verifies Blender 4.2+ binary discovery."""
    blender_bin = Universal3DEngine.find_blender_binary()
    assert blender_bin is not None
    assert Path(blender_bin).exists()


def test_runtime_checker_blender_detection():
    """AC-01: Verifies runtime_checker reports Blender capability."""
    caps = get_runtime_capabilities()
    assert "blender" in caps
    assert caps["blender"]["available"] is True
    assert "Blender" in caps["blender"]["version"]
    assert caps["blender_3d_capable"] is True

    report = format_doctor_report(caps)
    assert "Blender 3D" in report
    assert "3D Assets & Mockups (Blender) : [READY]" in report


def test_mcp_tool_annotations():
    """AC-05: Verifies omnipress_render_3d annotation standards."""
    assert "omnipress_render_3d" in MCP_TOOL_ANNOTATIONS
    ann = MCP_TOOL_ANNOTATIONS["omnipress_render_3d"]
    assert ann["readOnlyHint"] is False
    assert ann["destructiveHint"] is False
    assert ann["idempotentHint"] is True
    assert ann["openWorldHint"] is False
    assert "title" in ann


def test_render_invalid_template(tmp_path: Path):
    """Verifies that invalid template names raise ValueError."""
    engine = Universal3DEngine()
    out_file = tmp_path / "out.png"
    with pytest.raises(ValueError, match="Unknown 3D template"):
        engine.render(template="non_existent_template", output_path=out_file)


def test_render_recipe_execution(tmp_path: Path, test_texture_path: Path):
    """AC-02 & AC-03: Tests declarative recipe rendering for device_mockup."""
    engine = Universal3DEngine()
    out_file = tmp_path / "mockup_render.png"

    recipe = {
        "template": "device_mockup",
        "texture": str(test_texture_path),
        "output_name": "mockup_render.png",
        "resolution": "512x512",
        "samples": 8,
    }

    recipe_file = tmp_path / "recipe_3d.json"
    with open(recipe_file, "w", encoding="utf-8") as f:
        json.dump(recipe, f)

    res = engine.render_recipe(recipe=recipe_file)
    assert res["status"] == "success"
    out_path = Path(res["output_path"])
    assert out_path.exists()
    assert out_path.stat().st_size > 0

    # Verify rendered image has alpha channel and valid dimensions
    with Image.open(out_path) as img:
        assert img.mode == "RGBA"
        assert img.size == (512, 512)


def test_mcp_tool_direct_invocation(tmp_path: Path, test_texture_path: Path):
    """AC-05: Tests direct invocation of omnipress_render_3d MCP tool function."""
    out_filename = "test_mcp_render.png"
    res_str = omnipress_render_3d(
        template="device_mockup",
        output_filename=out_filename,
        texture_path=str(test_texture_path),
        resolution="512x512",
        samples=8,
    )
    res = json.loads(res_str)
    assert res["status"] == "success"
    out_path = Path(res["output_path"])
    assert out_path.exists()
    assert out_path.name == out_filename
