"""Declarative schema validation for OmniPress recipes and channel manifests.

Single source of truth: `.agents/schemas/*.schema.json` (JSON Schema Draft-07).
Engines call this validator before touching the filesystem or any external runtime.

Strictness is controlled by `OMNIPRESS_SCHEMA_STRICT` (default: "1").
Set it to "0" only for legacy workspaces during migration.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import jsonschema

logger = logging.getLogger("omnipress.schema_validator")

SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / ".agents" / "schemas"

KIND_SCHEMAS: Dict[str, str] = {
    "channel": "channel.schema.json",
    "carousel_recipe": "carousel_recipe.schema.json",
    "post_recipe": "post_recipe.schema.json",
    "thumbnail_recipe": "thumbnail_recipe.schema.json",
    "documentary_recipe": "documentary_recipe.schema.json",
    "caption_recipe": "caption_recipe.schema.json",
    "3d_recipe": "3d_recipe.schema.json",
    "template_manifest": "template_manifest.schema.json",
    "video_recipe": "video_recipe.schema.json",
    "audio_recipe": "audio_recipe.schema.json",
    "voice_recipe": "voice_recipe.schema.json",
    "image_recipe": "image_recipe.schema.json",
    "asset_recipe": "asset_recipe.schema.json",
}

_PLATFORM_RECIPE_PREFIXES = ("instagram", "linkedin", "x_", "twitter", "threads", "youtube", "tiktok", "reddit")

_schema_cache: Dict[str, tuple[tuple[int, int], Dict[str, Any]]] = {}


class SchemaValidationError(ValueError):
    """Raised when a declarative document violates its canonical schema."""

    def __init__(self, kind: str, errors: list[str], source: Optional[str] = None):
        self.kind = kind
        self.errors = errors
        self.source = source
        location = f" ({source})" if source else ""
        detail = "\n  - ".join(errors)
        super().__init__(f"Invalid {kind}{location}:\n  - {detail}")


def is_strict(strict: Optional[bool] = None) -> bool:
    if strict is not None:
        return strict
    raw = os.getenv("OMNIPRESS_SCHEMA_STRICT", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def load_schema(kind: str) -> Dict[str, Any]:
    """Loads (and mtime-caches) the JSON schema for a document kind."""
    if kind not in KIND_SCHEMAS:
        raise KeyError(f"Unknown schema kind '{kind}'. Known: {sorted(KIND_SCHEMAS)}")

    schema_path = SCHEMA_DIR / KIND_SCHEMAS[kind]
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found for kind '{kind}': {schema_path}")

    stat = schema_path.stat()
    signature = (stat.st_mtime_ns, stat.st_size)
    cached = _schema_cache.get(kind)
    if cached and cached[0] == signature:
        return cached[1]

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    _schema_cache[kind] = (signature, schema)
    return schema


def validate(
    kind: str,
    payload: Any,
    source: Optional[str] = None,
    strict: Optional[bool] = None,
) -> None:
    """Validates a payload against the schema of `kind`.

    In non-strict mode a violation is logged as a warning instead of raised.
    """
    schema = load_schema(kind)
    validator = jsonschema.Draft7Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(payload), key=lambda e: list(e.absolute_path)):
        location = ".".join(str(p) for p in err.absolute_path) or "$"
        errors.append(f"{location}: {err.message}")

    if not errors:
        return

    if source:
        errors = [f"{source}: {e}" for e in errors]

    if is_strict(strict):
        raise SchemaValidationError(kind, errors, source)

    logger.warning("Schema warning for %s%s: %s", kind, f" ({source})" if source else "", "; ".join(errors))


def validate_file(kind: str, path: Union[str, Path], strict: Optional[bool] = None) -> Dict[str, Any]:
    """Loads a JSON file and validates it. Returns the parsed payload."""
    file_path = Path(path).resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"Declarative file not found: {file_path}")
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}") from e
    validate(kind, payload, source=str(file_path), strict=strict)
    return payload


def infer_kind(path: Union[str, Path]) -> Optional[str]:
    """Infers a document kind from its filename, or None when ambiguous."""
    name = Path(path).name.lower()

    if name == "channel.json":
        return "channel"
    if name == "template.json":
        return "template_manifest"
    if name == "manifest.json":
        parent = Path(path).parent
        if (
            (parent / "template.py").is_file()
            or "templates_3d" in parent.parts
            or "blender_templates" in parent.parts
        ):
            return "template_manifest"
        return None
    if "thumbnail" in name and "recipe" in name:
        return "thumbnail_recipe"
    if "documentary" in name and "recipe" in name:
        return "documentary_recipe"
    if "caption" in name and "recipe" in name:
        return "caption_recipe"
    if ("3d" in name or "blender" in name) and "recipe" in name:
        return "3d_recipe"
    if "video" in name and "recipe" in name:
        return "video_recipe"
    if "audio" in name and "recipe" in name:
        return "audio_recipe"
    if "voice" in name and "recipe" in name:
        return "voice_recipe"
    if "image" in name and "recipe" in name:
        return "image_recipe"
    if "asset" in name and "recipe" in name:
        return "asset_recipe"
    if "carousel" in name and "recipe" in name:
        return "carousel_recipe"
    if name == "post_recipe.json":
        return "post_recipe"
    if "recipe" in name and name.startswith(_PLATFORM_RECIPE_PREFIXES):
        return "post_recipe"
    return None


def validate_recipe(
    path: Union[str, Path],
    kind: Optional[str] = None,
    strict: Optional[bool] = None,
) -> Optional[str]:
    """Validates a recipe file. Returns the resolved kind, or None if unknown."""
    resolved_kind = kind or infer_kind(path)
    if resolved_kind is None:
        logger.debug("No schema kind inferred for %s; skipping validation.", path)
        return None
    validate_file(resolved_kind, path, strict=strict)
    return resolved_kind
