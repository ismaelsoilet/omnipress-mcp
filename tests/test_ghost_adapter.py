"""Comprehensive unit tests for GhostPublisherAdapter (Admin API v5.0)."""

import os
import json
import base64
from unittest.mock import patch, MagicMock
import pytest
import requests

from src.adapters.ghost_adapter import GhostPublisherAdapter
from src.core.publishing_shield import PublishingShield


# Dummy 64-character hex secret for testing JWT generation
VALID_KEY_ID = "6501a2b3c4d5e6f708192a3b"
VALID_HEX_SECRET = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
VALID_ADMIN_KEY = f"{VALID_KEY_ID}:{VALID_HEX_SECRET}"
GHOST_URL = "https://my-blog.ghost.io"


@pytest.fixture
def temp_ledger(tmp_path, monkeypatch):
    """Sets a temporary path for the PublishingShield idempotency ledger."""
    ledger_file = tmp_path / "test_ghost_ledger.json"
    monkeypatch.setattr(PublishingShield, "get_ledger_path", lambda: ledger_file)
    return ledger_file


def test_ghost_is_configured(monkeypatch):
    """Verify is_configured strictly validates key format {id}:{secret} and URL."""
    monkeypatch.delenv("GHOST_ADMIN_API_KEY", raising=False)
    monkeypatch.delenv("GHOST_API_URL", raising=False)
    adapter = GhostPublisherAdapter()
    assert adapter.is_configured() is False

    # Key without colon
    adapter_bad = GhostPublisherAdapter(admin_api_key="invalid_no_colon", api_url=GHOST_URL)
    assert adapter_bad.is_configured() is False

    # Valid key and URL
    adapter_ok = GhostPublisherAdapter(admin_api_key=VALID_ADMIN_KEY, api_url=GHOST_URL)
    assert adapter_ok.is_configured() is True


def test_ghost_jwt_token_generation():
    """Verify JWT conforms to Ghost Admin API specification (HS256, aud=/admin/, exp=5m)."""
    adapter = GhostPublisherAdapter(admin_api_key=VALID_ADMIN_KEY, api_url=GHOST_URL)
    token = adapter._generate_jwt_token()

    parts = token.split(".")
    assert len(parts) == 3, "JWT must consist of header.payload.signature"

    # Decode header
    header_padded = parts[0] + "=" * ((4 - len(parts[0]) % 4) % 4)
    header = json.loads(base64.urlsafe_b64decode(header_padded).decode("utf-8"))
    assert header["alg"] == "HS256"
    assert header["typ"] == "JWT"
    assert header["kid"] == VALID_KEY_ID

    # Decode payload
    payload_padded = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
    payload = json.loads(base64.urlsafe_b64decode(payload_padded).decode("utf-8"))
    assert payload["aud"] == "/admin/"
    assert payload["exp"] - payload["iat"] == 300

    # Malformed non-hex secret raises ValueError
    adapter_bad_hex = GhostPublisherAdapter(admin_api_key=f"{VALID_KEY_ID}:not_a_hex_secret!", api_url=GHOST_URL)
    with pytest.raises(ValueError, match="not valid hexadecimal"):
        adapter_bad_hex._generate_jwt_token()


def test_ghost_markdown_to_html():
    """Verify markdown headings, lists, bold, blockquotes, and code fences are converted."""
    md = (
        "# Título Principal\n\n"
        "## Subtítulo Importante\n\n"
        "Este é um texto com **negrito** e *itálico*.\n\n"
        "> Citação relevante de segurança.\n\n"
        "- Item de lista 1\n"
        "- Item de lista 2\n\n"
        "```python\ndef test(): pass\n```"
    )
    html = GhostPublisherAdapter._markdown_to_html(md)
    assert "<h1>Título Principal</h1>" in html
    assert "<h2>Subtítulo Importante</h2>" in html
    assert "<strong>negrito</strong>" in html
    assert "<em>itálico</em>" in html
    assert "<blockquote><p>Citação relevante de segurança.</p></blockquote>" in html
    assert "<ul>" in html
    assert "<li>Item de lista 1</li>" in html
    assert "<pre><code>" in html
    assert "def test(): pass" in html


def test_ghost_publish_draft_success(temp_ledger):
    """Verify successful Ghost draft creation with mock 201 response."""
    adapter = GhostPublisherAdapter(admin_api_key=VALID_ADMIN_KEY, api_url=GHOST_URL)

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "posts": [
            {
                "id": "post_ghost_67890",
                "title": "Decifrando o Protocolo MCP",
                "url": "https://my-blog.ghost.io/decifrando-o-protocolo-mcp/",
                "status": "draft",
            }
        ]
    }

    with patch("requests.post", return_value=mock_resp) as mock_post:
        res = adapter.publish_article(
            title="Decifrando o Protocolo MCP",
            content_markdown="# Introdução\n\nTexto sobre MCP.",
            category="mcp",
            tags=["mcp", "ai", "agents"],
            published=False,
            canonical_url="https://omnipress.suitplus.com.br/articles/mcp",
        )

        assert res["success"] is True
        assert res["id"] == "post_ghost_67890"
        assert res["status"] == "draft"
        assert res["provider"] == "ghost"

        # Check call arguments
        calls = mock_post.call_args_list
        assert len(calls) == 1
        headers = calls[0][1]["headers"]
        assert headers["Authorization"].startswith("Ghost ")
        assert headers["Accept-Version"] == "v5.0"
        payload = calls[0][1]["json"]["posts"][0]
        assert payload["title"] == "Decifrando o Protocolo MCP"
        assert payload["status"] == "draft"
        assert payload["canonical_url"] == "https://omnipress.suitplus.com.br/articles/mcp"
        assert {"name": "mcp"} in payload["tags"]


def test_ghost_publish_live_success(temp_ledger):
    """Verify published=True sets status='published'."""
    adapter = GhostPublisherAdapter(admin_api_key=VALID_ADMIN_KEY, api_url=GHOST_URL)

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "posts": [
            {
                "id": "post_live_123",
                "title": "Post Ao Vivo",
                "url": "https://my-blog.ghost.io/post-ao-vivo/",
                "status": "published",
            }
        ]
    }

    with patch("requests.post", return_value=mock_resp):
        res = adapter.publish_article(
            title="Post Ao Vivo",
            content_markdown="Conteúdo ao vivo.",
            published=True,
        )
        assert res["success"] is True
        assert res["status"] == "published"


def test_ghost_error_responses(temp_ledger):
    """Verify error handling for 401 Unauthorized and 422 Unprocessable."""
    adapter = GhostPublisherAdapter(admin_api_key=VALID_ADMIN_KEY, api_url=GHOST_URL)

    # 401 Unauthorized
    resp_401 = MagicMock()
    resp_401.status_code = 401
    with patch("requests.post", return_value=resp_401):
        res = adapter.publish_article(title="Artigo", content_markdown="Corpo...")
        assert res["success"] is False
        assert res["status_code"] == 401
        assert "authentication rejected" in res["error"].lower()

    # 422 Validation Error
    resp_422 = MagicMock()
    resp_422.status_code = 422
    resp_422.text = '{"errors": [{"message": "Validation error, cannot edit post."}]}'
    with patch("requests.post", return_value=resp_422):
        res = adapter.publish_article(title="Artigo", content_markdown="Corpo...")
        assert res["success"] is False
        assert res["status_code"] == 422


def test_ghost_publishing_shield_anti_duplicate(temp_ledger):
    """Verify PublishingShield prevents duplicate article dispatches to Ghost CMS."""
    adapter = GhostPublisherAdapter(admin_api_key=VALID_ADMIN_KEY, api_url=GHOST_URL)

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "posts": [{"id": "post_ghost_dup_999", "url": "https://my-blog.ghost.io/dup/"}]
    }

    with patch("requests.post", return_value=mock_resp) as mock_post:
        # First publication succeeds
        res1 = adapter.publish_article(
            title="Prevenção de Duplicatas no Ghost",
            content_markdown="Conteúdo único para validação de idempotência no Ghost CMS.",
        )
        assert res1["success"] is True
        assert mock_post.call_count == 1

        # Second publication is blocked by shield
        res2 = adapter.publish_article(
            title="Prevenção de Duplicatas no Ghost",
            content_markdown="Conteúdo único para validação de idempotência no Ghost CMS.",
        )
        assert res2["success"] is False
        assert res2.get("blocked_by_shield") is True
        assert mock_post.call_count == 1

        # Force duplicate passes
        res3 = adapter.publish_article(
            title="Prevenção de Duplicatas no Ghost",
            content_markdown="Conteúdo único para validação de idempotência no Ghost CMS.",
            force_duplicate=True,
        )
        assert res3["success"] is True
        assert mock_post.call_count == 2


def test_ghost_channel_scoped_credentials(monkeypatch):
    """Verify GhostPublisherAdapter resolves channel-specific credentials via ChannelManager."""
    monkeypatch.delenv("GHOST_ADMIN_API_KEY", raising=False)
    monkeypatch.delenv("GHOST_API_URL", raising=False)
    adapter = GhostPublisherAdapter(admin_api_key="", api_url="")
    assert adapter.is_configured() is False

    def mock_get_cred(key, slug):
        if key == "GHOST_ADMIN_API_KEY":
            return VALID_ADMIN_KEY
        if key == "GHOST_API_URL":
            return "https://channel-blog.ghost.io"
        return ""

    with patch("src.core.channel_manager.ChannelManager.get_credential", side_effect=mock_get_cred):
        assert adapter.is_configured(channel_slug="my-channel") is True
        key, url = adapter.get_credentials(channel_slug="my-channel")
        assert key == VALID_ADMIN_KEY
        assert url == "https://channel-blog.ghost.io"

