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


def test_cli_verify_posts_command(capsys, monkeypatch):
    """Verify omnipress verify-posts invokes engine and formats output."""
    from unittest.mock import MagicMock
    mock_engine = MagicMock()
    mock_engine.verify_post_execution.return_value = {
        "success": True,
        "summary": {"sent": 1, "scheduled": 2, "error": 0},
        "results": [
            {
                "post_id": "test_1",
                "platform": "linkedin",
                "status": "sent",
                "execution_state": "SUCCESS_SENT",
                "due_at": "2026-10-30T12:15:00Z",
            }
        ],
    }

    monkeypatch.setattr("src.engine.universal_publisher.UniversalPublisherEngine", lambda **kw: mock_engine)
    code = main(["verify-posts", "--post", "sample_post", "--channel", "test_channel"])
    assert code == 0
    captured = capsys.readouterr()
    assert "OmniPress Post Execution Health Check" in captured.out
    assert "SENT (LIVE)" in captured.out


def test_cli_meta_auth_list_only(capsys):
    """Verify omnipress meta-auth --list-only."""
    with patch("src.core.meta_asset_manager.MetaAssetManager.inspect_token") as mock_inspect, \
         patch("src.core.meta_asset_manager.MetaAssetManager.fetch_assets") as mock_fetch:
        mock_inspect.return_value = {"valid": True, "user_id": "u1", "user_name": "Test User"}
        mock_fetch.return_value = {
            "success": True,
            "total_fetched": 1,
            "total_matching": 1,
            "assets": [
                {
                    "page_id": "p123",
                    "page_name": "Minha Página",
                    "instagram": {"username": "meu_ig", "id": "ig123"},
                }
            ],
        }
        code = main(["meta-auth", "--token", "test_tok", "--list-only", "--channel", "test-channel"])
        assert code == 0
        captured = capsys.readouterr()
        assert "Meta Sign-In & Asset Manager" in captured.out
        assert "Minha Página" in captured.out
