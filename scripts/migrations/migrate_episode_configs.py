#!/usr/bin/env python3
"""One-time migration: episode_config.json -> documentary_recipe.json (manifest mode).

Existing documentary episodes already have final, pre-rendered scene cards. This
tool captures them as a declarative manifest (no re-rendering, no double text),
so the generation scripts can be retired without losing the episode definition.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHANNEL_DIR = PROJECT_ROOT / "channels" / "dossie-historico"
REPORT_PATH = PROJECT_ROOT / "docs" / "MIGRATION_DOCUMENTARY.md"

_CAMERA = {
    "zoom-in": "slow_zoom_in",
    "zoom-out": "slow_zoom_out",
    "pan-left": "pan_left",
    "pan-right": "pan_right",
    "dramatic-push": "slow_zoom_in",
    "snap-zoom": "slow_zoom_in",
    "tilt-down": "static",
    "subtle-zoom": "static",
}

_TRANSITION = {
    "fade": "cut",
    "whip-pan": "whip_pan",
    "shutter-flash": "flash",
    "cross-dissolve": "dissolve",
}


def _resolve_media(media_src: str, episode_dir: Path) -> Optional[Path]:
    candidate = Path(str(media_src))
    if candidate.is_absolute() and candidate.is_file():
        return candidate
    roots = [
        episode_dir / "documentario",
        episode_dir / "documentario" / "midias",
        episode_dir / "midias",
        CHANNEL_DIR / "media" / "visuals" / "documentary" / episode_dir.name / "scenes",
        CHANNEL_DIR,
        PROJECT_ROOT / "public",
    ]
    for root in roots:
        found = root / candidate
        if found.is_file():
            return found
        found = root / candidate.name
        if found.is_file():
            return found
    return None


def migrate(dry_run: bool = True) -> Dict[str, Any]:
    migrated: List[Dict[str, Any]] = []
    missing: List[str] = []

    for config_path in sorted(CHANNEL_DIR.glob("episodios/*/documentario/episode_config.json")):
        episode_dir = config_path.parent.parent
        data = json.loads(config_path.read_text(encoding="utf-8"))
        scenes: List[Dict[str, Any]] = []

        for scene in data.get("scenes") or []:
            media = _resolve_media(scene.get("mediaSrc", ""), episode_dir)
            if not media:
                missing.append(f"{episode_dir.name}: {scene.get('mediaSrc')}")
                continue
            scenes.append(
                {
                    "id": scene.get("id", f"scene_{len(scenes)+1:02d}"),
                    "type": "ken_burns",
                    "media": str(media),
                    "duration_seconds": scene.get("durationInSeconds", 6.0),
                    "start_seconds": scene.get("startInSeconds", 0.0),
                    "headline": scene.get("headline", ""),
                    "subheadline": scene.get("subheadline", ""),
                    "badge": scene.get("badge", ""),
                    "camera": _CAMERA.get(str(scene.get("cameraDirection")), "static"),
                    "transition": _TRANSITION.get(str(scene.get("transitionType")), "cut"),
                }
            )

        if not scenes:
            continue

        intro = data.get("introProps") or {}
        recipe = {
            "$schema": "../../../../../.agents/schemas/documentary_recipe.schema.json",
            "channel_slug": "dossie-historico",
            "episode_slug": episode_dir.name,
            "title": data.get("title", episode_dir.name),
            "language": data.get("language", "pt"),
            "aspect_ratio": "16:9",
            "mode": "manifest",
            "theme": {
                "primary": intro.get("primaryColor", ""),
                "accent": intro.get("primaryColor", ""),
                "background": intro.get("backgroundColor", ""),
            },
            "scenes": scenes,
            "audio": {
                "soundtrack": data.get("backgroundMusicSrc", ""),
                "soundtrack_volume": data.get("backgroundMusicVolume", 0.16),
            },
            "outputs": {"episode_config": "episode_config.generated.json"},
        }

        recipe_path = config_path.parent / "documentary_recipe.json"
        if not dry_run:
            recipe_path.write_text(
                json.dumps(recipe, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        migrated.append(
            {
                "episode": episode_dir.name,
                "recipe": str(recipe_path),
                "scenes": len(scenes),
            }
        )

    return {"episodes": migrated, "missing": missing}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = migrate(dry_run=args.dry_run)

    lines = [
        "# Migração — Episódios documentais para receitas declarativas",
        "",
        f"Modo: {'dry-run' if args.dry_run else 'escrita'}",
        "",
        "> **Nota de versionamento:** `channels/*` é ignorado pelo git (apenas `_template/` é",
        "> versionado). As receitas e os manifests gerados vivem localmente no workspace do canal.",
        "> O modo `manifest` referencia as cenas finais já renderizadas, sem reaplicar texto.",
        "",
        "| Episódio | Cenas | Recipe |",
        "|---|---:|---|",
    ]
    for item in result["episodes"]:
        lines.append(f"| `{item['episode']}` | {item['scenes']} | `{item['recipe']}` |")
    if result["missing"]:
        lines.extend(["", "## Assets não encontrados", ""])
        lines.extend(f"- {item}" for item in result["missing"])
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
