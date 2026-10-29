#!/usr/bin/env python3
"""One-time migration: dossie-historico carousel scripts -> declarative recipes.

This is a migration tool, not a production renderer (Rule 12). It resolves the
module-level slide list (including `str(BRAIN_DIR / "asset.jpg")` expressions)
and the sibling schedule script, then writes `carrossel/carousel_recipe.json`.

Usage:
  python scripts/migrations/migrate_dossie_to_recipes.py --dry-run
  python scripts/migrations/migrate_dossie_to_recipes.py --force
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHANNEL_DIR = PROJECT_ROOT / "channels" / "dossie-historico"
REPORT_PATH = PROJECT_ROOT / "docs" / "MIGRATION_DOSSIE.md"

_ASSET_KEYS = ("bg_image_path", "filename", "bg_name", "image_asset")


@dataclass
class EpisodeMigration:
    carousel_dir: Path
    episode_dir: Path
    render_script: Path
    schedule_script: Optional[Path]
    slides: List[Dict[str, Any]] = field(default_factory=list)
    aspect_ratio: str = "3:4"
    card_bg_alpha: Optional[int] = None
    caption: str = ""
    schedule_time: Optional[str] = None
    platforms: List[str] = field(default_factory=lambda: ["instagram"])
    mode: str = "customScheduled"
    missing_assets: List[str] = field(default_factory=list)

    @property
    def post_slug(self) -> str:
        return self.episode_dir.name

    @property
    def recipe_path(self) -> Path:
        return self.carousel_dir / "carousel_recipe.json"


def _path_namespace(text: str, script_path: Path) -> Dict[str, str]:
    namespace: Dict[str, str] = {}
    for match in re.finditer(r'^([A-Z_][A-Z0-9_]*)\s*=\s*Path\("([^"]+)"\)', text, re.M):
        namespace[match.group(1)] = match.group(2)
    for match in re.finditer(
        r'^([A-Z_][A-Z0-9_]*)\s*=\s*Path\(__file__\)\.resolve\(\)((?:\.parent)+)',
        text,
        re.M,
    ):
        depth = match.group(2).count(".parent")
        base = script_path
        for _ in range(depth):
            base = base.parent
        namespace[match.group(1)] = str(base)
    return namespace


def _resolve_path_expressions(text: str, script_path: Path) -> str:
    """Rewrites `VAR / "a" / "b"` and `str(...)` into literal strings before AST parsing."""
    namespace = _path_namespace(text, script_path)

    def join_segments(variable: str, raw_segments: str) -> str:
        segments = re.findall(r'"([^"]*)"', raw_segments)
        if not segments:
            return '""'
        if variable in namespace:
            return json.dumps(str(Path(namespace[variable]).joinpath(*segments)))
        return json.dumps(segments[-1])

    # Bare path expressions (used in tuple-based slide lists).
    text = re.sub(
        r'([A-Z_][A-Z0-9_]*)\s*((?:/\s*"[^"]*")+)',
        lambda m: join_segments(m.group(1), m.group(2)),
        text,
    )
    # Wrapped in str(...) or Path(...).
    text = re.sub(r'(?:str|Path)\(\s*("(?:[^"\\]|\\.)*")\s*\)', r"\1", text)
    return text


def _literal_slides(tree: ast.AST) -> Optional[List[Dict[str, Any]]]:
    candidates: List[List[Dict[str, Any]]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, (ast.List, ast.Tuple)):
            continue
        try:
            value = ast.literal_eval(node.value)
        except Exception:
            continue
        if (
            isinstance(value, (list, tuple))
            and value
            and isinstance(value[0], dict)
            and "headline" in value[0]
        ):
            candidates.append(list(value))
            continue
        # Tuple-based custom renderers: (bg, out_brain, out_asset, badge, headline, body, page, swipe, gradient)
        if (
            isinstance(value, (list, tuple))
            and value
            and isinstance(value[0], (tuple, list))
            and len(value[0]) >= 8
            and isinstance(value[0][4], str)
        ):
            converted = []
            for row in value:
                converted.append(
                    {
                        "bg_image_path": row[0],
                        "badge_text": row[3],
                        "headline": row[4],
                        "body": row[5],
                        "page_str": row[6],
                        "swipe_str": row[7],
                    }
                )
            candidates.append(converted)
    if not candidates:
        return None
    return max(candidates, key=len)


def _render_kwargs(tree: ast.AST) -> Dict[str, Any]:
    found: Dict[str, Any] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func_name = getattr(node.func, "attr", getattr(node.func, "id", ""))
        if func_name not in ("render_slide", "build_carousel"):
            continue
        for keyword in node.keywords:
            if keyword.arg in ("aspect_ratio", "card_bg_alpha"):
                try:
                    found[keyword.arg] = ast.literal_eval(keyword.value)
                except Exception:
                    continue
    return found


def _extract_caption(text: str) -> str:
    match = re.search(r'caption\s*=\s*(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', text, re.S)
    if match:
        return match.group(1).strip()
    match = re.search(r'caption\s*=\s*"((?:[^"\\]|\\.)*)"', text, re.S)
    if match:
        return match.group(1).strip()
    return ""


def _extract_schedule(text: str) -> Dict[str, Any]:
    schedule: Dict[str, Any] = {}
    match = re.search(r'schedule_time\s*=\s*"([^"]+)"', text)
    if match:
        schedule["schedule_time"] = match.group(1)
    match = re.search(r'platforms\s*=\s*(\[[^\]]*\])', text)
    if match:
        try:
            schedule["platforms"] = ast.literal_eval(match.group(1))
        except Exception:
            pass
    match = re.search(r'mode\s*=\s*"([^"]+)"', text)
    if match:
        schedule["mode"] = match.group(1)
    return schedule


def _asset_path(migration: EpisodeMigration, slide: Dict[str, Any]) -> Optional[Path]:
    carousel_dir = migration.carousel_dir
    search_roots = [
        carousel_dir / "midias" / "raw",
        carousel_dir / "midias",
        carousel_dir,
        CHANNEL_DIR / "media" / "raw",
        CHANNEL_DIR / "media" / "visuals",
        PROJECT_ROOT / "media" / "assets",
        PROJECT_ROOT / "media" / "historical",
    ]

    for key in _ASSET_KEYS:
        raw = slide.get(key)
        if not raw:
            continue
        candidate = Path(str(raw))
        if candidate.is_absolute() and candidate.is_file():
            return candidate
        for root in search_roots:
            found = root / candidate.name
            if found.is_file():
                return found
    return None


def _portable_asset(
    migration: EpisodeMigration,
    asset: Path,
    recipe_dir: Path,
    dry_run: bool,
) -> Path:
    """Returns an asset path relative to the recipe, copying external files in."""
    try:
        return asset.relative_to(recipe_dir)
    except ValueError:
        pass

    target_dir = migration.carousel_dir / "midias" / "raw"
    target = target_dir / asset.name
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.stat().st_size != asset.stat().st_size:
            shutil.copy2(asset, target)
    return target.relative_to(recipe_dir)


def _build_recipe(migration: EpisodeMigration, dry_run: bool = True) -> Dict[str, Any]:
    recipe_path = migration.recipe_path
    slides: List[Dict[str, Any]] = []

    for index, slide in enumerate(migration.slides, start=1):
        asset = _asset_path(migration, slide)
        entry: Dict[str, Any] = {
            "headline": slide.get("headline", ""),
            "body": slide.get("body", ""),
            "badge_text": slide.get("badge_text", ""),
            "swipe_str": slide.get(
                "swipe_str", "" if index < len(migration.slides) else "Salve & Siga"
            ),
        }
        if asset:
            entry["bg_image"] = str(
                _portable_asset(migration, asset, recipe_path.parent, dry_run)
            )
        else:
            migration.missing_assets.append(
                str(slide.get("bg_image_path") or slide.get("filename") or slide.get("bg_name"))
            )
        if slide.get("top_bias") is not None:
            entry["top_bias"] = slide["top_bias"]
        if slide.get("image_asset"):
            entry["image_asset"] = slide["image_asset"]
        if slide.get("layout"):
            entry["layout"] = slide["layout"]
        slides.append(entry)

    recipe: Dict[str, Any] = {
        "$schema": "../../../../.agents/schemas/carousel_recipe.schema.json",
        "channel_slug": "dossie-historico",
        "post_slug": migration.post_slug,
        "aspect_ratio": migration.aspect_ratio,
        "preset": "classic_card",
        "slides": slides,
    }
    if migration.card_bg_alpha is not None:
        recipe["layout_parameters"] = {"card_bg_alpha": migration.card_bg_alpha}
    if migration.caption:
        recipe["publish"] = {
            "caption": migration.caption,
            "platforms": migration.platforms,
            "mode": migration.mode,
        }
        if migration.schedule_time:
            recipe["publish"]["schedule_time"] = migration.schedule_time
    return recipe


def _find_episode_groups() -> Dict[Path, Dict[str, List[Path]]]:
    groups: Dict[Path, Dict[str, List[Path]]] = {}
    for script in CHANNEL_DIR.glob("episodios/*/carrossel/scripts/*.py"):
        carousel_dir = script.parent.parent
        groups.setdefault(carousel_dir, {"render": [], "schedule": []})
        if script.name.startswith(("render_", "generate_")):
            groups[carousel_dir]["render"].append(script)
        elif script.name.startswith(("schedule_", "publish_")):
            groups[carousel_dir]["schedule"].append(script)
    return groups


def migrate(dry_run: bool = True, force: bool = False) -> List[EpisodeMigration]:
    results: List[EpisodeMigration] = []
    for carousel_dir, scripts in sorted(_find_episode_groups().items()):
        best: Optional[EpisodeMigration] = None
        for script in sorted(scripts["render"]):
            source = script.read_text(encoding="utf-8")
            prepared = _resolve_path_expressions(source, script)
            try:
                tree = ast.parse(prepared)
            except SyntaxError:
                continue
            slides = _literal_slides(tree)
            if not slides:
                continue
            kwargs = _render_kwargs(tree)
            candidate = EpisodeMigration(
                carousel_dir=carousel_dir,
                episode_dir=carousel_dir.parent,
                render_script=script,
                schedule_script=scripts["schedule"][0] if scripts["schedule"] else None,
                slides=slides,
                aspect_ratio=str(kwargs.get("aspect_ratio") or "3:4"),
                card_bg_alpha=kwargs.get("card_bg_alpha"),
            )
            if best is None or len(candidate.slides) > len(best.slides):
                best = candidate

        if best is None:
            continue

        if best.schedule_script:
            schedule_text = best.schedule_script.read_text(encoding="utf-8")
            best.caption = _extract_caption(schedule_text)
            schedule = _extract_schedule(schedule_text)
            best.schedule_time = schedule.get("schedule_time")
            best.platforms = schedule.get("platforms", best.platforms)
            best.mode = schedule.get("mode", best.mode)

        recipe = _build_recipe(best, dry_run=dry_run)
        if not dry_run and (force or not best.recipe_path.exists()):
            best.recipe_path.write_text(
                json.dumps(recipe, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        results.append(best)

    return results


def write_report(results: List[EpisodeMigration], dry_run: bool) -> None:
    lines = [
        "# Migração — dossie-historico para receitas declarativas",
        "",
        f"Modo: {'dry-run' if dry_run else 'escrita'}",
        "",
        "> **Nota de versionamento:** `channels/*` é ignorado pelo git (apenas `_template/` é",
        "> versionado). As receitas geradas vivem localmente no workspace do canal. Os scripts",
        "> removidos foram substituídos pelas receitas e pelo motor universal; o conteúdo",
        "> editorial (slides e legendas) está preservado nos JSONs.",
        "",
        f"Episódios migrados: **{len(results)}**",
        "",
        "| Episódio | Script | Slides | Assets faltando | Publish |",
        "|---|---|---:|---:|---|",
    ]
    for item in results:
        publish = "sim" if item.caption else "não"
        lines.append(
            f"| `{item.post_slug}` | `{item.render_script.name}` | {len(item.slides)} | "
            f"{len(item.missing_assets)} | {publish} |"
        )

    lines.extend(["", "## Substituição por comandos universais", ""])
    lines.append("```bash")
    lines.append("# Renderiza e publica cada carrossel migrado:")
    lines.append(
        "uv run omnipress carousel --recipe channels/dossie-historico/episodios/<ep>/carrossel/carousel_recipe.json --all"
    )
    lines.append("```")
    lines.extend(
        [
            "",
            "## Scripts legados ainda pendentes",
            "",
            "Os scripts de áudio, captions, thumbnails, shorts e utilitários que ainda não",
            "foram migrados estão inventariados em [`docs/LEGACY_SCRIPTS.md`](./LEGACY_SCRIPTS.md),",
            "com o comando/engine universal que deve substituí-los antes da remoção.",
        ]
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_existing_recipes() -> List[EpisodeMigration]:
    """Builds the report from recipes when the source scripts are already gone."""
    results: List[EpisodeMigration] = []
    for recipe_path in sorted(CHANNEL_DIR.glob("episodios/*/carrossel/carousel_recipe.json")):
        data = json.loads(recipe_path.read_text(encoding="utf-8"))
        carousel_dir = recipe_path.parent
        publish = data.get("publish") or {}
        results.append(
            EpisodeMigration(
                carousel_dir=carousel_dir,
                episode_dir=carousel_dir.parent,
                render_script=Path("(migrated)"),
                schedule_script=None,
                slides=list(data.get("slides") or []),
                aspect_ratio=data.get("aspect_ratio", "3:4"),
                caption=publish.get("caption", ""),
                schedule_time=publish.get("schedule_time"),
                platforms=publish.get("platforms", ["instagram"]),
                mode=publish.get("mode", "customScheduled"),
            )
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate dossie carousel scripts to recipes")
    parser.add_argument("--dry-run", action="store_true", help="Analyze without writing recipes")
    parser.add_argument("--force", action="store_true", help="Overwrite existing recipes")
    args = parser.parse_args()

    results = migrate(dry_run=args.dry_run, force=args.force)
    if not results:
        results = _load_existing_recipes()
    write_report(results, dry_run=args.dry_run)

    total_slides = sum(len(item.slides) for item in results)
    missing = sum(len(item.missing_assets) for item in results)
    published = sum(1 for item in results if item.caption)
    print(
        json.dumps(
            {
                "mode": "dry-run" if args.dry_run else "write",
                "episodes": len(results),
                "slides": total_slides,
                "episodes_with_publish": published,
                "missing_assets": missing,
                "report": str(REPORT_PATH),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
