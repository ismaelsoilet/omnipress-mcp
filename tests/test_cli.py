"""Unit tests for OmniPress CLI commands."""

import pytest
from unittest.mock import patch
from src.cli import main


def test_cli_doctor(capsys):
    """Verify omnipress doctor outputs diagnostic report and returns 0."""
    code = main(["doctor"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Environment Diagnostic" in captured.out
    assert "Python Runtime" in captured.out


def test_cli_status(capsys):
    """Verify omnipress status reports channels and ledger."""
    code = main(["status"])
    assert code == 0
    captured = capsys.readouterr()
    assert "System Status" in captured.out
    assert "Active Channel Workspace" in captured.out


def test_cli_setup_non_interactive(capsys, tmp_path, monkeypatch):
    """Verify omnipress setup --non-interactive executes cleanly."""
    monkeypatch.setattr("src.cli.PROJECT_ROOT", tmp_path)
    # create sample .env.example in tmp_path
    (tmp_path / ".env.example").write_text("BUFFER_API_KEY=\n", encoding="utf-8")

    code = main(["setup", "--non-interactive"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Interactive Setup Wizard" in captured.out
    assert (tmp_path / ".env").exists()


def test_cli_no_args_shows_help(capsys):
    """Verify running omnipress without args displays help and returns 0."""
    code = main([])
    assert code == 0
    captured = capsys.readouterr()
    assert "usage:" in captured.out.lower() or "omnipress" in captured.out.lower()
