"""Unit and integration tests for MetaAssetManager (asset discovery, filtering, and channel binding)."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from src.core.meta_asset_manager import MetaAssetManager
from src.core.channel_manager import ChannelManager


@pytest.fixture
def temp_channel_workspace(tmp_path):
    cm = ChannelManager(root_dir=tmp_path)
    cm.create_channel(
        slug="meu-dossie",
        name="Meu Dossiê",
        handle="@meudossie",
        category="history",
    )
    return {"cm": cm, "root": tmp_path, "slug": "meu-dossie"}


def test_inspect_token_valid():
    mam = MetaAssetManager()
    with patch("requests.get") as mock_get:
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"id": "user_12345", "name": "Ismael Soilet"}
        mock_get.return_value = resp

        res = mam.inspect_token("valid_token_123")
        assert res["valid"] is True
        assert res["user_id"] == "user_12345"
        assert res["user_name"] == "Ismael Soilet"


def test_inspect_token_invalid():
    mam = MetaAssetManager()
    with patch("requests.get") as mock_get:
        resp = MagicMock(status_code=400)
        resp.json.return_value = {"error": {"message": "Invalid OAuth access token.", "code": 190}}
        mock_get.return_value = resp

        res = mam.inspect_token("bad_token")
        assert res["valid"] is False
        assert "Invalid OAuth" in res["error"]


def test_fetch_assets_pagination_and_query_filtering():
    mam = MetaAssetManager()

    page_1_data = {
        "data": [
            {
                "id": "page_100",
                "name": "Dossiê Histórico Oficial",
                "category": "Media",
                "access_token": "page_token_100",
                "instagram_business_account": {
                    "id": "ig_999",
                    "username": "dossiehistorico",
                    "name": "Dossiê Histórico",
                },
            },
            {
                "id": "page_200",
                "name": "Página Aleatória de Culinária",
                "category": "Food",
                "access_token": "page_token_200",
            },
        ],
        "paging": {
            "cursors": {"after": "cursor_page_2"},
            "next": "https://graph.facebook.com/v19.0/me/accounts?after=cursor_page_2",
        },
    }

    page_2_data = {
        "data": [
            {
                "id": "page_300",
                "name": "Ismael Soilet Consultoria",
                "category": "Consulting",
                "access_token": "page_token_300",
                "instagram_business_account": {
                    "id": "ig_777",
                    "username": "ismaelsoilet",
                    "name": "Ismael Soilet",
                },
            }
        ],
        "paging": {
            "cursors": {},
        },
    }

    with patch("requests.get") as mock_get:
        resp1 = MagicMock(status_code=200)
        resp1.json.return_value = page_1_data

        resp2 = MagicMock(status_code=200)
        resp2.json.return_value = page_2_data

        mock_get.side_effect = [resp1, resp2]

        # 1. Fetch with query "dossie"
        res = mam.fetch_assets(token="tok_meta", query="dossie", max_pages=5)
        assert res["success"] is True
        assert res["total_fetched"] == 3
        assert res["total_matching"] == 1
        assert res["assets"][0]["page_name"] == "Dossiê Histórico Oficial"
        assert res["assets"][0]["instagram"]["username"] == "dossiehistorico"


def test_bind_asset_to_channel_writes_env(temp_channel_workspace):
    mam = MetaAssetManager(root_dir=temp_channel_workspace["root"])
    channel_slug = temp_channel_workspace["slug"]

    page_detail = {
        "id": "page_100",
        "name": "Dossiê Histórico Oficial",
        "access_token": "perpetual_page_token_100",
        "instagram_business_account": {
            "id": "ig_999",
            "username": "dossiehistorico",
            "name": "Dossiê Histórico",
        },
    }

    with patch("requests.get") as mock_get:
        resp = MagicMock(status_code=200)
        resp.json.return_value = page_detail
        mock_get.return_value = resp

        res = mam.bind_asset_to_channel(
            channel_slug=channel_slug,
            user_token="user_token_abc",
            page_id="page_100",
        )

        assert res["success"] is True
        assert res["facebook"]["page_id"] == "page_100"
        assert res["instagram"]["account_id"] == "ig_999"

        # Verify .env on disk
        env_file = Path(res["env_path"])
        assert env_file.exists()
        content = env_file.read_text(encoding="utf-8")
        assert 'FACEBOOK_PAGE_ID="page_100"' in content
        assert 'FACEBOOK_ACCESS_TOKEN="perpetual_page_token_100"' in content
        assert 'INSTAGRAM_ACCOUNT_ID="ig_999"' in content
        assert 'INSTAGRAM_USERNAME="dossiehistorico"' in content

        # Verify ChannelManager resolves the credentials
        cm = ChannelManager(root_dir=temp_channel_workspace["root"])
        assert cm.get_credential("FACEBOOK_PAGE_ID", channel_slug) == "page_100"
        assert cm.get_credential("INSTAGRAM_ACCOUNT_ID", channel_slug) == "ig_999"
        assert cm.get_credential("INSTAGRAM_ACCESS_TOKEN", channel_slug) == "perpetual_page_token_100"


def test_get_oauth_login_url():
    mam = MetaAssetManager()
    url = mam.get_oauth_login_url(app_id="123456789")
    assert "https://www.facebook.com/v19.0/dialog/oauth" in url
    assert "client_id=123456789" in url
    assert "pages_manage_posts" in url
    assert "instagram_content_publish" in url


def test_exchange_code_for_token():
    mam = MetaAssetManager()
    with patch("requests.get") as mock_get:
        resp_short = MagicMock(status_code=200)
        resp_short.json.return_value = {"access_token": "short_token_123"}

        resp_long = MagicMock(status_code=200)
        resp_long.json.return_value = {
            "access_token": "long_token_456",
            "expires_in": 5184000,
            "token_type": "bearer",
        }

        mock_get.side_effect = [resp_short, resp_long]

        res = mam.exchange_code_for_token("code_xyz", "app_1", "sec_2")
        assert res["success"] is True
        assert res["access_token"] == "long_token_456"
        assert res["is_long_lived"] is True
