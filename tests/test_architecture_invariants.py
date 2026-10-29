"""Rule 14 architectural invariants enforced in CI.

These tests fail the build if channel identity leaks back into `src/`, if an
engine spawns a subprocess outside the provider layer, or if a component keeps
request state in a mutable instance attribute.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
CHANNELS = ROOT / "channels"

_IGNORED_DIRS = {"default", "test-channel"}
# `template-channel` is the documented slug of channels/_template (not a real brand).
_IGNORED_SLUGS = {"template-channel"}


def _channel_slugs() -> set[str]:
    return {
        path.name
        for path in CHANNELS.iterdir()
        if path.is_dir()
        and not path.name.startswith("_")
        and path.name not in _IGNORED_DIRS
        and path.name not in _IGNORED_SLUGS
    }


def _source_files() -> list[Path]:
    suffixes = {".py", ".ts", ".tsx", ".json"}
    return [
        path
        for path in SRC.rglob("*")
        if path.is_file() and path.suffix in suffixes
    ]


def test_no_channel_slugs_in_src():
    slugs = _channel_slugs()
    offenders = []
    for path in _source_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for slug in slugs:
            if slug in text:
                offenders.append(f"{path.relative_to(ROOT)} contains channel slug '{slug}'")
    assert not offenders, "\n".join(offenders)


def test_no_channel_identity_branches():
    pattern = re.compile(r"channel_slug\s*==|channel_slug\s+in\s+\[|slug\s*==\s*[\"']")
    offenders = []
    for path in _source_files():
        if path.suffix != ".py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if pattern.search(text):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"Channel identity branch found in: {offenders}"


def test_no_channel_path_literals_in_src():
    pattern = re.compile(r"[\"']channels/")
    offenders = []
    for path in _source_files():
        if path.suffix != ".py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if pattern.search(text):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"Hardcoded channels/ path in: {offenders}"


def test_adapters_do_not_read_channel_credentials_from_env():
    credential_prefixes = (
        "BUFFER_",
        "DEVTO_",
        "GHOST_",
        "INSTAGRAM_",
        "REDDIT_",
        "YOUTUBE_",
        "OMNIPRESS_WEBHOOK_",
        "S3_",
        "AWS_",
    )
    pattern = re.compile(
        r"os\.getenv\(\s*[\"'](" + "|".join(re.escape(p) for p in credential_prefixes) + r")"
    )
    offenders = []
    for path in (SRC / "adapters").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in pattern.finditer(text):
            offenders.append(f"{path.relative_to(ROOT)} reads {match.group(1)} directly")
    assert not offenders, "\n".join(offenders)


def test_engines_and_adapters_are_stateless():
    """No `self.x = ...` assignments outside __init__ in engines and adapters."""
    offenders = []
    for base in (SRC / "engine", SRC / "adapters"):
        for path in base.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for cls in [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]:
                for fn in [
                    node
                    for node in cls.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name != "__init__"
                ]:
                    for node in ast.walk(fn):
                        targets = []
                        if isinstance(node, ast.Assign):
                            targets = node.targets
                        elif isinstance(node, ast.AnnAssign):
                            targets = [node.target]
                        for target in targets:
                            if (
                                isinstance(target, ast.Attribute)
                                and isinstance(target.value, ast.Name)
                                and target.value.id == "self"
                            ):
                                offenders.append(
                                    f"{path.relative_to(ROOT)}:{node.lineno} "
                                    f"{cls.name}.{fn.name} assigns self.{target.attr}"
                                )
    assert not offenders, "\n".join(offenders)


def test_no_subprocess_outside_provider_layer():
    pattern = re.compile(r"\bsubprocess\.(run|Popen|check_call|check_output|call)\b")
    providers_dir = SRC / "engine" / "providers"
    offenders = []
    for path in (SRC / "engine").rglob("*.py"):
        if providers_dir in path.parents:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if pattern.search(text):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"Subprocess outside providers/: {offenders}"


def test_no_channel_brand_template_in_core():
    assert not (SRC / "engine" / "templates_3d" / "brazil_flag").exists()
    assert not (SRC / "engine" / "blender_templates" / "brazil_flag.py").exists()


def test_remotion_components_have_no_brand_color_literals():
    forbidden = ("#D4AF37", "212, 175, 55")
    offenders = []
    for path in (SRC / "video").rglob("*.tsx"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for literal in forbidden:
            if literal in text:
                offenders.append(f"{path.relative_to(ROOT)} contains {literal}")
    assert not offenders, "\n".join(offenders)


def test_remotion_theme_module_exists():
    assert (SRC / "video" / "theme.ts").is_file()
