"""Universal 3D Engine for OmniPress MCP.

Provides declarative 3D asset generation powered by headless Blender 4.2+ LTS.
Supports photorealistic device mockups, rotating badges/coins, and kinetic 3D typography
for social media carousels, articles, and Remotion video compositions.
Complies with Rule 07, Rule 10, and Rule 12.
"""

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.core.channel_manager import ChannelManager

logger = logging.getLogger("omnipress.universal_3d")

TEMPLATES_DIR = Path(__file__).resolve().parent / "blender_templates"


class BlenderRenderError(Exception):
    """Raised when Blender headless rendering fails."""
    pass


class Universal3DEngine:
    """Universal declarative 3D rendering engine for OmniPress."""

    AVAILABLE_TEMPLATES = {
        "device_mockup": TEMPLATES_DIR / "device_mockup.py",
        "rotating_badge": TEMPLATES_DIR / "rotating_badge.py",
        "kinetic_title": TEMPLATES_DIR / "kinetic_title.py",
        "waving_flag": TEMPLATES_DIR / "waving_flag.py",
        "brazil_flag": TEMPLATES_DIR / "waving_flag.py",  # Backward-compatible alias
    }

    def __init__(self, channel_manager: Optional[ChannelManager] = None):
        self.channel_manager = channel_manager or ChannelManager()
        self.blender_bin = self.find_blender_binary()

    @classmethod
    def find_blender_binary(cls) -> Optional[str]:
        """Locates the Blender executable on PATH or standard local user paths."""
        which_bin = shutil.which("blender")
        if which_bin:
            return which_bin

        # Check standard user local paths
        candidates = [
            Path.home() / ".local" / "bin" / "blender",
            Path("/usr/local/bin/blender"),
            Path("/usr/bin/blender"),
            Path("/snap/bin/blender"),
        ]
        for cand in candidates:
            if cand.is_file() and os.access(cand, os.X_OK):
                return str(cand)

        return None

    def is_available(self) -> bool:
        """Returns True if Blender binary is installed and executable."""
        return self.blender_bin is not None

    def get_template_script(self, template_name: str) -> Path:
        """Resolves the python template script path."""
        if template_name in self.AVAILABLE_TEMPLATES:
            script_path = self.AVAILABLE_TEMPLATES[template_name]
            if script_path.exists():
                return script_path

        # Also support direct path or file name
        cand = Path(template_name)
        if cand.is_file():
            return cand
        cand_in_dir = TEMPLATES_DIR / f"{template_name}.py"
        if cand_in_dir.is_file():
            return cand_in_dir

        available = list(self.AVAILABLE_TEMPLATES.keys())
        raise ValueError(f"Unknown 3D template: '{template_name}'. Available: {available}")

    def render(
        self,
        template: str,
        output_path: Union[str, Path],
        texture: Optional[Union[str, Path]] = None,
        text: Optional[str] = None,
        material: Optional[str] = None,
        resolution: str = "1080x1080",
        engine: str = "BLENDER_EEVEE_NEXT",
        samples: int = 32,
        extra_args: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 180,
    ) -> Path:
        """
        Renders a 3D asset via Blender headless.

        Args:
            template: Name of template (e.g. 'device_mockup', 'rotating_badge', 'kinetic_title')
            output_path: Destination file path for rendered PNG
            texture: Optional path to texture image (for device screen or coin emblem)
            text: Optional text string for kinetic_title
            material: Optional material preset (e.g. 'gold', 'silver', 'chrome', 'obsidian')
            resolution: Render dimensions (e.g. '1080x1080', '1920x1080', '1080x1920')
            engine: Blender render engine ('BLENDER_EEVEE_NEXT' or 'CYCLES')
            samples: Render sampling count
            extra_args: Additional template-specific parameters
            timeout_seconds: Subprocess timeout limit

        Returns:
            Path to the rendered output image file.
        """
        if not self.is_available():
            raise BlenderRenderError(
                "Blender binary not found. Install Blender 4.2+ LTS to use 3D rendering."
            )

        script_path = self.get_template_script(template)
        out_path = Path(output_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.blender_bin,
            "-b",
            "-P",
            str(script_path),
            "--",
            "--output",
            str(out_path),
            "--resolution",
            resolution,
            "--engine",
            engine,
            "--samples",
            str(samples),
        ]

        if texture:
            tex_path = Path(texture).resolve()
            if not tex_path.exists():
                logger.warning(f"Texture path does not exist: {tex_path}")
            cmd.extend(["--texture", str(tex_path)])

        if text:
            cmd.extend(["--text", text])

        if material:
            cmd.extend(["--material", material])

        if extra_args:
            for k, v in extra_args.items():
                flag = f"--{k.replace('_', '-')}"
                cmd.extend([flag, str(v)])

        logger.info(f"Running Blender 3D render: {' '.join(cmd)}")
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as e:
            raise BlenderRenderError(f"Blender render timed out after {timeout_seconds}s") from e

        if res.returncode != 0:
            err_msg = res.stderr or res.stdout
            logger.error(f"Blender execution error: {err_msg}")
            raise BlenderRenderError(f"Blender render failed (code {res.returncode}): {err_msg[:400]}")

        if not out_path.exists():
            raise BlenderRenderError(f"Render completed but output file not found: {out_path}")

        logger.info(f"3D asset rendered successfully: {out_path}")
        return out_path

    def render_recipe(
        self,
        recipe: Union[str, Path, Dict[str, Any]],
        channel_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes a declarative 3D recipe (JSON/Dict) complying with Rule 12.

        Example Recipe:
        {
            "template": "device_mockup",
            "texture": "channels/<slug>/media/carousels/slide_01.png",
            "output_name": "hero_phone_mockup.png",
            "resolution": "1080x1080",
            "engine": "BLENDER_EEVEE_NEXT",
            "samples": 32
        }
        """
        if isinstance(recipe, (str, Path)):
            recipe_file = Path(recipe).resolve()
            if not recipe_file.exists():
                raise FileNotFoundError(f"Recipe file not found: {recipe_file}")
            with open(recipe_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            base_dir = recipe_file.parent
        else:
            data = recipe
            base_dir = Path.cwd()

        template = data.get("template", "device_mockup")
        resolution = data.get("resolution", "1080x1080")
        engine = data.get("engine", "BLENDER_EEVEE_NEXT")
        samples = int(data.get("samples", 32))
        material = data.get("material")
        text = data.get("text")
        output_name = data.get("output_name", f"{template}_render.png")

        # Resolve output directory
        target_slug = channel_slug or data.get("channel_slug")
        if target_slug:
            ch_dir = self.channel_manager.get_channel_dir(target_slug)
            out_dir = ch_dir / "media" / "visuals" / "3d"
        else:
            out_dir = base_dir / "output_3d"

        out_path = out_dir / output_name

        # Resolve texture if provided
        texture = data.get("texture")
        if texture:
            tex_candidate = Path(texture)
            if not tex_candidate.is_absolute():
                tex_candidate = (base_dir / tex_candidate).resolve()
            texture = str(tex_candidate)

        rendered_file = self.render(
            template=template,
            output_path=out_path,
            texture=texture,
            text=text,
            material=material,
            resolution=resolution,
            engine=engine,
            samples=samples,
            extra_args=data.get("extra_args"),
        )

        return {
            "status": "success",
            "output_path": str(rendered_file),
            "template": template,
            "resolution": resolution,
            "engine": engine,
            "file_size_bytes": rendered_file.stat().st_size if rendered_file.exists() else 0,
        }
