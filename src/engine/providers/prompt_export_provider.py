"""Prompt export provider: always-available fallback for external AI generators.

Writes structured, production-ready prompts (Midjourney, FLUX, Stable Diffusion,
Ideogram, Leonardo) with exact aspect ratio flags and target paths, so image
quota exhaustion never blocks a channel deliverable (Rule 10).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.engine.providers.base import ProviderError, RenderProvider, register

_MODEL_FLAGS = {
    "midjourney": "--ar",
    "flux": "aspect_ratio",
    "stable_diffusion": "aspect_ratio",
    "ideogram": "aspect_ratio",
    "leonardo": "aspect_ratio",
}


@register
class PromptExportProvider(RenderProvider):
    name = "prompt_export"
    capability = "python"
    supports = frozenset({"image"})
    default_extension = "json"

    def validate(self, spec: Dict[str, Any]) -> List[str]:
        errors = super().validate(spec)
        errors.extend(self.check_required(spec, ["prompt"]))
        return errors

    def render(self, spec: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
        errors = self.validate(spec)
        if errors:
            raise ProviderError("; ".join(errors))

        base = Path(out_dir).resolve()
        base.mkdir(parents=True, exist_ok=True)

        aspect = str(spec.get("aspect_ratio") or "16:9")
        targets = spec.get("external_targets") or ["midjourney", "flux", "stable_diffusion", "ideogram", "leonardo"]
        prompt = str(spec["prompt"])
        negative = str(spec.get("negative_prompt") or "")
        output_hint = str(spec.get("output") or "generated.png")

        exports: Dict[str, Any] = {}
        for target in targets:
            target = str(target)
            flag = _MODEL_FLAGS.get(target, "aspect_ratio")
            if target == "midjourney":
                rendered = f"{prompt} --ar {aspect} --style raw --v 6"
            else:
                rendered = f"{prompt} [{flag}={aspect}]"
            exports[target] = {"prompt": rendered, "negative_prompt": negative}

        manifest = {
            "status": "success",
            "provider": self.name,
            "reason": "AI image generation unavailable; prompts exported for external rendering.",
            "aspect_ratio": aspect,
            "target_save_path": str(base / output_hint),
            "prompts": exports,
        }

        json_path = base / "prompt_export.json"
        json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        md_lines = [
            f"# Prompt Export — {aspect}",
            "",
            f"**Target save path:** `{base / output_hint}`",
            "",
        ]
        for target, payload in exports.items():
            md_lines.extend([f"## {target}", "", "```text", payload["prompt"], "```", ""])
            if negative:
                md_lines.extend(["Negative prompt:", "```text", negative, "```", ""])
        md_path = base / "prompt_export.md"
        md_path.write_text("\n".join(md_lines), encoding="utf-8")

        manifest["export_files"] = [str(json_path), str(md_path)]
        return manifest
