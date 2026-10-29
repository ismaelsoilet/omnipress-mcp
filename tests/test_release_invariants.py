"""Rule 13 release invariants: version synchronization and changelog quality."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _pyproject_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    assert match, "version not found in pyproject.toml"
    return match.group(1)


def test_version_is_synchronized_across_canonical_files():
    version = _pyproject_version()

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert package["version"] == version

    package_lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
    assert package_lock["version"] == version
    assert package_lock["packages"][""]["version"] == version

    server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    assert server["version"] == version
    assert server["packages"][0]["version"] == version

    plugin = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    assert plugin["version"] == version

    openapi = json.loads((ROOT / "config/openapi.json").read_text(encoding="utf-8"))
    assert openapi["info"]["version"] == version

    init_text = (ROOT / "src" / "__init__.py").read_text(encoding="utf-8")
    assert f'__version__ = "{version}"' in init_text

    cli_text = (ROOT / "src" / "cli.py").read_text(encoding="utf-8")
    assert f"OmniPress MCP {version}" in cli_text

    server_text = (ROOT / "src" / "server.py").read_text(encoding="utf-8")
    assert f'"version": "{version}"' in server_text


def test_changelog_top_entry_matches_version():
    version = _pyproject_version()
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(r"^##\s*\[([0-9]+\.[0-9]+\.[0-9]+)\]\s*—\s*\d{4}-\d{2}-\d{2}\s*$", changelog, re.M)
    assert match, "CHANGELOG.md must start with '## [x.y.z] — YYYY-MM-DD'"
    assert match.group(1) == version


def test_changelog_uses_keep_a_changelog_sections():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    top = changelog.split("## [", 2)[1]
    assert re.search(r"^### (Added|Changed|Fixed|Deprecated|Removed|Security)$", top, re.M)


def test_required_documentation_exists():
    for relative in (
        "README.md",
        "README.pt-BR.md",
        "CHANGELOG.md",
        "docs/AGENT_MANUAL.md",
        "docs/ARCHITECTURE.md",
        "docs/PROVIDERS.md",
    ):
        assert (ROOT / relative).is_file(), f"Missing required documentation: {relative}"
