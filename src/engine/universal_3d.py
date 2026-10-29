"""Universal 3D Engine.

Declarative 3D rendering via the `blender` provider. Templates are discovered by
manifest (builtin generic primitives + channel-specific templates), never by a
hardcoded registry, and no arbitrary script path is accepted from a recipe.
"""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.core.capabilities import resolve_blender_binary
from src.core.channel_manager import ChannelManager
from src.core.schema_validator import validate as validate_schema
from src.engine.providers.base import ProviderError
from src.engine.providers.blender_provider import BlenderProvider

logger = logging.getLogger("omnipress.universal_3d")

BUILTIN_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates_3d"


class BlenderRenderError(Exception):
    """Raised when Blender headless rendering fails (backward-compatible)."""


class Universal3DEngine:
    """Universal, manifest-driven 3D rendering engine."""

    def __init__(self, channel_manager: Optional[ChannelManager] = None):
        self.channel_manager = channel_manager or ChannelManager()
        self.provider = BlenderProvider()

    @classmethod
    def find_blender_binary(cls, channel_slug: Optional[str] = None) -> Optional[str]:
        """Locates the Blender executable (env -> channel -> PATH -> standard paths)."""
        return resolve_blender_binary(channel_slug)

    def is_available(self, channel_slug: Optional[str] = None) -> bool:
        return self.find_blender_binary(channel_slug) is not None

    # ------------------------------------------------------------------
    # Template registry
    # ------------------------------------------------------------------
    def _template_roots(self, channel_slug: Optional[str] = None) -> List[Path]:
        roots: List[Path] = []
        if channel_slug:
            roots.append(self.channel_manager.get_channel_dir(channel_slug) / "blender_templates")
        roots.append(BUILTIN_TEMPLATES_DIR)
        return roots

    def list_templates(self, channel_slug: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Discovers templates by manifest. Channel templates override builtins."""
        templates: Dict[str, Dict[str, Any]] = {}
        for root in reversed(self._template_roots(channel_slug)):
            if not root.is_dir():
                continue
            for manifest_path in sorted(root.glob("*/manifest.json")):
                script_path = manifest_path.parent / "template.py"
                if not script_path.is_file():
                    continue
                try:
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                name = str(manifest.get("name") or manifest_path.parent.name)
                templates[name] = {
                    **manifest,
                    "name": name,
                    "script_path": str(script_path),
                    "manifest_path": str(manifest_path),
                    "source": str(manifest_path.parent),
                }
        return templates

    def resolve_template(
        self,
        template_name: str,
        channel_slug: Optional[str] = None,
    ) -> Tuple[Path, Dict[str, Any]]:
        """Resolves a registered template and enforces the channel allowlist."""
        name = str(template_name or "").strip()
        if not name:
            raise ValueError("3D template name is required.")

        if name == "brazil_flag":
            raise ValueError(
                "Template 'brazil_flag' was removed from the core. Add it as a channel "
                "template under channels/<slug>/blender_templates/ instead."
            )

        if Path(name).name != name or name.startswith("."):
            raise ValueError(
                f"Unknown 3D template: '{name}'. Template paths are not accepted; "
                "register the template under a manifest.json."
            )

        templates = self.list_templates(channel_slug)
        if name not in templates:
            raise ValueError(
                f"Unknown 3D template: '{name}'. Available: {sorted(templates)}"
            )

        channel = self.channel_manager.get_channel(channel_slug) if channel_slug else {}
        allowlist = (
            ((channel or {}).get("render") or {}).get("blender") or {}
        ).get("template_allowlist") or []
        if allowlist and name not in allowlist:
            raise ValueError(
                f"Template '{name}' is not in the allowlist for channel '{channel_slug}': {allowlist}"
            )

        entry = templates[name]
        return Path(entry["script_path"]), entry

    def get_template_script(self, template_name: str, channel_slug: Optional[str] = None) -> Path:
        """Backward-compatible: returns the registered template script path."""
        script, _ = self.resolve_template(template_name, channel_slug)
        return script

    # ------------------------------------------------------------------
    # Asset + parameter resolution
    # ------------------------------------------------------------------
    def _resolve_asset(
        self,
        value: str,
        channel_slug: Optional[str],
        recipe_dir: Optional[Path],
    ) -> str:
        candidate = Path(str(value))
        if candidate.is_absolute():
            return str(candidate)
        if recipe_dir and (recipe_dir / candidate).is_file():
            return str((recipe_dir / candidate).resolve())
        if channel_slug:
            channel_dir = self.channel_manager.get_channel_dir(channel_slug)
            for base in (
                channel_dir / "media" / "raw",
                channel_dir / "media" / "visuals",
                channel_dir / "recursos_globais" / "fontes",
                channel_dir,
            ):
                if (base / candidate).is_file():
                    return str((base / candidate).resolve())
        return str(candidate.resolve())

    @staticmethod
    def _validate_params(
        params: Dict[str, Any],
        declared_list: List[Dict[str, Any]],
    ) -> List[str]:
        errors: List[str] = []
        declared = {str(p.get("name")): p for p in declared_list if p.get("name")}

        for name in sorted(set(params) - set(declared)):
            errors.append(f"unknown template parameter '{name}'")

        for name, spec in declared.items():
            if spec.get("required") and params.get(name) in (None, ""):
                errors.append(f"missing required template parameter '{name}'")
                continue
            if name not in params or params[name] is None:
                continue
            value = params[name]
            expected = spec.get("type")
            if expected == "number" and not isinstance(value, (int, float)):
                errors.append(f"parameter '{name}' must be a number")
            elif expected == "integer" and not isinstance(value, int):
                errors.append(f"parameter '{name}' must be an integer")
            elif expected == "boolean" and not isinstance(value, bool):
                errors.append(f"parameter '{name}' must be a boolean")
            elif expected == "string" and not isinstance(value, str):
                errors.append(f"parameter '{name}' must be a string")
            if spec.get("enum") and value not in spec["enum"]:
                errors.append(f"parameter '{name}' must be one of {spec['enum']}")
            if expected in ("number", "integer") and isinstance(value, (int, float)):
                if spec.get("min") is not None and value < spec["min"]:
                    errors.append(f"parameter '{name}' must be >= {spec['min']}")
                if spec.get("max") is not None and value > spec["max"]:
                    errors.append(f"parameter '{name}' must be <= {spec['max']}")
        return errors

    # ------------------------------------------------------------------
    # Recipe execution
    # ------------------------------------------------------------------
    def render_recipe(
        self,
        recipe: Union[str, Path, Dict[str, Any]],
        channel_slug: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Executes a declarative 3D recipe (Rule 12)."""
        recipe_dir: Optional[Path] = None
        if isinstance(recipe, (str, Path)):
            recipe_path = Path(recipe).resolve()
            if not recipe_path.is_file():
                raise FileNotFoundError(f"Recipe file not found: {recipe_path}")
            data = json.loads(recipe_path.read_text(encoding="utf-8"))
            recipe_dir = recipe_path.parent
        else:
            data = dict(recipe)

        validate_schema("3d_recipe", data, source=str(recipe_dir or "<dict>"))

        target_slug = channel_slug or data.get("channel_slug") or self.channel_manager.get_active_channel_slug()
        channel = self.channel_manager.get_channel(target_slug) or {}
        blender_cfg = ((channel.get("render") or {}).get("blender") or {}) if channel else {}

        template_name = str(data.get("template") or "")
        script_path, manifest = self.resolve_template(template_name, target_slug)
        if not self.is_available():
            raise BlenderRenderError(
                "Blender binary not found. Install Blender 4.2+ LTS or set BLENDER_PATH."
            )

        params = dict(data.get("params") or {})
        for key in ("texture", "text", "material", "font"):
            if data.get(key) is not None:
                params.setdefault(key, data[key])
        theme = data.get("theme") or {}
        declared_list = manifest.get("params") or []
        declared_names = {str(p.get("name")) for p in declared_list}
        for theme_key in ("primary", "accent", "background"):
            if theme.get(theme_key) and f"theme_{theme_key}" in declared_names:
                params.setdefault(f"theme_{theme_key}", theme[theme_key])

        errors = self._validate_params(params, declared_list)
        if errors:
            raise ValueError("; ".join(errors))

        if dry_run:
            return {
                "status": "valid",
                "engine": "universal_3d",
                "template": template_name,
                "template_source": manifest.get("source"),
                "params": params,
                "blender_available": self.is_available(),
            }

        for asset_key in ("texture", "font"):
            if params.get(asset_key):
                params[asset_key] = self._resolve_asset(str(params[asset_key]), target_slug, recipe_dir)

        aspect = data.get("aspect_ratio")
        resolution = (
            data.get("resolution")
            or (blender_cfg.get("resolution_by_ratio") or {}).get(aspect)  # type: ignore[union-attr]
            or "1080x1080"
        )

        post_slug = str(data.get("post_slug") or template_name or "render")
        if channel:
            out_dir = self.channel_manager.get_channel_dir(target_slug) / "media" / "visuals" / "3d" / post_slug
        else:
            out_dir = ((recipe_dir or Path.cwd()) / "output_3d" / post_slug)

        spec = {
            "channel_slug": target_slug if channel else None,
            "script_path": str(script_path),
            "output_name": data.get("output_name"),
            "format": data.get("format") or "png",
            "supported_formats": manifest.get("outputs") or ["png"],
            "resolution": resolution,
            "engine": data.get("engine") or blender_cfg.get("engine") or "BLENDER_EEVEE_NEXT",
            "samples": int(data.get("samples") or blender_cfg.get("samples") or 32),
            "fps": data.get("fps") or 30,
            "duration_seconds": data.get("duration_seconds") or 1,
            "transparent": data.get("transparent", blender_cfg.get("transparent_default", True)),
            "color_management": data.get("color_management") or blender_cfg.get("color_management"),
            "params": params,
            "timeout_seconds": data.get("timeout_seconds") or 300,
        }

        try:
            result = self.provider.render(spec, out_dir)
        except ProviderError as exc:
            raise BlenderRenderError(str(exc)) from exc

        manifest_record = {
            "status": "success",
            "engine": "universal_3d",
            "channel_slug": target_slug,
            "template": template_name,
            "template_source": manifest.get("source"),
            "params": params,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            **{k: v for k, v in result.items() if k != "status"},
        }
        manifest_path = Path(out_dir) / "render_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest_record, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        manifest_record["render_manifest"] = str(manifest_path)

        if channel:
            manifest_record["public_path"] = str(Path(result["output_path"]))
        return manifest_record

    # ------------------------------------------------------------------
    # Legacy API
    # ------------------------------------------------------------------
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
        channel_slug: Optional[str] = None,
    ) -> Path:
        """Legacy single-asset render API (kept for CLI/MCP backward compatibility)."""
        out_path = Path(output_path).resolve()
        script_path, manifest = self.resolve_template(template, channel_slug)

        if not self.is_available():
            raise BlenderRenderError(
                "Blender binary not found. Install Blender 4.2+ LTS or set BLENDER_PATH."
            )

        params = dict(extra_args or {})
        for key, value in (("texture", texture), ("text", text), ("material", material)):
            if value:
                params.setdefault(key, str(value))

        errors = self._validate_params(params, manifest.get("params") or [])
        if errors:
            raise ValueError("; ".join(errors))

        spec = {
            "channel_slug": channel_slug,
            "script_path": str(script_path),
            "output_name": out_path.name,
            "format": "png",
            "supported_formats": manifest.get("outputs") or ["png"],
            "resolution": resolution,
            "engine": engine,
            "samples": samples,
            "params": params,
            "timeout_seconds": timeout_seconds,
        }
        try:
            result = self.provider.render(spec, out_path.parent)
        except ProviderError as exc:
            raise BlenderRenderError(str(exc)) from exc
        return Path(result["output_path"])
