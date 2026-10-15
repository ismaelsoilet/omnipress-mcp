"""Comprehensive unit tests for DevToPublisherAdapter."""

import os
from unittest.mock import patch, MagicMock
import pytest
import requests

from src.adapters.devto_adapter import DevToPublisherAdapter
from src.core.publishing_shield import PublishingShield


@pytest.fixture
def temp_ledger(tmp_path, monkeypatch):
    """Sets a temporary path for the PublishingShield idempotency ledger."""
    ledger_file = tmp_path / "test_devto_ledger.json"
    monkeypatch.setattr(PublishingShield, "get_ledger_path", lambda: ledger_file)
    return ledger_file


def test_devto_is_configured(monkeypatch):
    """Verify is_configured reflects DEVTO_API_KEY presence."""
    monkeypatch.delenv("DEVTO_API_KEY", raising=False)
    adapter = DevToPublisherAdapter()
    assert adapter.is_configured() is False

    monkeypatch.setenv("DEVTO_API_KEY", "devto_secret_token_123")
    adapter_configured = DevToPublisherAdapter()
    assert adapter_configured.is_configured() is True


def test_devto_tag_sanitization():
    """Verify Dev.to tag rules: lowercase alphanumeric + underscore, max 4 tags."""
    adapter = DevToPublisherAdapter(api_key="dummy")
    raw_tags = ["Python 3.12", "DevSecOps!", "Open-Source", "#Cloud", "ExtraTag5", "ExtraTag6"]
    cleaned = adapter._sanitize_tags(raw_tags)
    assert len(cleaned) == 4
    assert cleaned == ["python312", "devsecops", "opensource", "cloud"]


def test_devto_publish_draft_success(temp_ledger, monkeypatch):
    """Verify successful article draft creation with mock 201 response."""
    monkeypatch.setenv("DEVTO_API_KEY", "mock_key")
    adapter = DevToPublisherAdapter()

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "id": 987654,
        "title": "Arquitetura Hexagonal com FastMCP e Python",
        "url": "https://dev.to/omnipress/arquitetura-hexagonal-fastmcp-987654",
    }

    with patch("requests.post", return_value=mock_resp) as mock_post:
        res = adapter.publish_article(
            title="Arquitetura Hexagonal com FastMCP e Python",
            content_markdown="# Introdução\n\nEste artigo explora FastMCP...",
            category="python",
            tags=["python", "architecture", "mcp"],
            published=False,
            canonical_url="https://omnipress.suitplus.com.br/articles/fastmcp",
        )

        assert res["success"] is True
        assert res["id"] == "987654"
        assert res["status"] == "draft"
        assert res["provider"] == "devto"

        # Verify request parameters
        calls = mock_post.call_args_list
        assert len(calls) == 1
        headers = calls[0][1]["headers"]
        assert headers["api-key"] == "mock_key"
        payload = calls[0][1]["json"]["article"]
        assert payload["title"] == "Arquitetura Hexagonal com FastMCP e Python"
        assert payload["published"] is False
        assert payload["canonical_url"] == "https://omnipress.suitplus.com.br/articles/fastmcp"
        assert payload["tags"] == ["python", "architecture", "mcp"]


def test_devto_publish_live_success(temp_ledger):
    """Verify published=True sends published=True in payload and reports published status."""
    adapter = DevToPublisherAdapter(api_key="mock_key")

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "id": 112233,
        "title": "Publicação Imediata no Dev.to",
        "url": "https://dev.to/omnipress/publicacao-imediata-112233",
    }

    with patch("requests.post", return_value=mock_resp):
        res = adapter.publish_article(
            title="Publicação Imediata no Dev.to",
            content_markdown="Conteúdo publicado ao vivo.",
            published=True,
        )
        assert res["success"] is True
        assert res["status"] == "published"


def test_devto_api_error_responses(temp_ledger):
    """Verify appropriate error dicts for 401 Unauthorized, 422 Unprocessable, and 500."""
    adapter = DevToPublisherAdapter(api_key="invalid_key")

    # 401 Unauthorized
    resp_401 = MagicMock()
    resp_401.status_code = 401
    with patch("requests.post", return_value=resp_401):
        res = adapter.publish_article(title="Artigo", content_markdown="Corpo...")
        assert res["success"] is False
        assert res["status_code"] == 401
        assert "unauthorized" in res["error"].lower()

    # 422 Validation Error
    resp_422 = MagicMock()
    resp_422.status_code = 422
    resp_422.text = '{"error": "Title has already been taken"}'
    with patch("requests.post", return_value=resp_422):
        res = adapter.publish_article(title="Artigo", content_markdown="Corpo...")
        assert res["success"] is False
        assert res["status_code"] == 422
        assert "validation error" in res["error"].lower()

    # Network Exception
    with patch("requests.post", side_effect=requests.exceptions.ConnectTimeout("Connection timed out")):
        res = adapter.publish_article(title="Artigo", content_markdown="Corpo...")
        assert res["success"] is False
        assert "Network error" in res["error"]


def test_devto_publishing_shield_anti_duplicate(temp_ledger):
    """Verify PublishingShield prevents duplicate article dispatches to Dev.to."""
    adapter = DevToPublisherAdapter(api_key="mock_key")

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"id": 555111, "url": "https://dev.to/article/555111"}

    with patch("requests.post", return_value=mock_resp) as mock_post:
        # First publication succeeds
        res1 = adapter.publish_article(
            title="Prevenção de Duplicatas no Dev.to",
            content_markdown="Conteúdo idêntico para verificação de idempotência no ledger.",
        )
        assert res1["success"] is True
        assert mock_post.call_count == 1

        # Second publication with identical title and content must be blocked by shield
        res2 = adapter.publish_article(
            title="Prevenção de Duplicatas no Dev.to",
            content_markdown="Conteúdo idêntico para verificação de idempotência no ledger.",
        )
        assert res2["success"] is False
        assert res2.get("blocked_by_shield") is True
        assert mock_post.call_count == 1  # Network was NOT hit a second time

        # Third publication with force_duplicate=True bypasses the shield
        res3 = adapter.publish_article(
            title="Prevenção de Duplicatas no Dev.to",
            content_markdown="Conteúdo idêntico para verificação de idempotência no ledger.",
            force_duplicate=True,
        )
        assert res3["success"] is True
        assert mock_post.call_count == 2


def test_devto_unsupported_social_post():
    """Verify queue_social_post returns an explicit error indicating Dev.to is article-only."""
    adapter = DevToPublisherAdapter(api_key="mock_key")
    res = adapter.queue_social_post(text="Tweet curto", platforms=["devto"])
    assert res["success"] is False
    assert "only supports long-form articles" in res["error"]
