"""Agent harness compatibility contract tests."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_opencode_local_mcp_config():
    config = _load("opencode.json")
    server = config["mcp"]["omnipress"]
    assert server["type"] == "local"
    assert server["enabled"] is True
    command = " ".join(server["command"])
    assert "src.server" in command
    assert server["environment"]["OMNIPRESS_ACTIVE_CHANNEL"] == "default"


def test_command_code_project_mcp_config():
    config = _load(".mcp.json")
    server = config["mcpServers"]["omnipress"]
    assert server["transport"] == "stdio"
    assert server["command"].endswith("python")
    assert server["args"] == ["-m", "src.server"]
    assert server["env"]["OMNIPRESS_ACTIVE_CHANNEL"] == "default"


def test_antigravity_workspace_mcp_config():
    config = _load(".agents/mcp_config.json")
    server = config["mcpServers"]["omnipress"]
    assert server["command"].endswith("python")
    assert server["args"] == ["-m", "src.server"]
    assert server["env"]["OMNIPRESS_ACTIVE_CHANNEL"] == "default"

    shim = _load("mcp_config.json")
    assert "omnipress" in shim["mcpServers"]


def test_agent_compatibility_docs_cover_all_harnesses():
    text = (ROOT / "docs" / "AGENT_COMPATIBILITY.md").read_text(encoding="utf-8")
    assert "Antigravity" in text
    assert "Command Code" in text
    assert "OpenCode" in text
    assert "omnipress studio" in text
    assert "omnipress_prepare_editable_video" in text
