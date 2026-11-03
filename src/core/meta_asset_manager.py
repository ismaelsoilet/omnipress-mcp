"""Meta Asset & Authentication Manager for OmniPress (Multi-Asset Discovery & Channel Binding)."""

import os
import re
import requests
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class MetaAssetManager:
    """
    Manages Meta authentication, asset discovery (Facebook Pages & linked Instagram Professional accounts),
    and binding to specific OmniPress channels with atomic .env persistence and live verification.
    Engineered for accounts managing hundreds or thousands of pages and assets.
    """

    GRAPH_API_VERSION = "v19.0"
    BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = Path(root_dir or PROJECT_ROOT).resolve()

    def inspect_token(self, token: str) -> Dict[str, Any]:
        """
        Validates the provided Meta Access Token against the Graph API.
        Returns user identity, app metadata, or actionable error diagnostics.
        """
        clean_token = (token or "").strip()
        if not clean_token:
            return {"valid": False, "error": "Token is empty."}

        url = f"{self.BASE_URL}/me"
        params = {"fields": "id,name"}
        headers = {"Authorization": f"Bearer {clean_token}"}

        try:
            res = requests.get(url, params=params, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                return {
                    "valid": True,
                    "user_id": data.get("id"),
                    "user_name": data.get("name"),
                }
            err = res.json().get("error", {})
            return {
                "valid": False,
                "status_code": res.status_code,
                "error": err.get("message", res.text),
                "error_type": err.get("type"),
                "code": err.get("code"),
                "subcode": err.get("error_subcode"),
            }
        except requests.RequestException as exc:
            return {"valid": False, "error": f"Network exception verifying Meta token: {str(exc)}"}

    def fetch_assets(
        self,
        token: str,
        query: Optional[str] = None,
        limit_per_page: int = 100,
        max_pages: int = 10,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Lists Facebook Pages and linked Instagram Business accounts accessible by the token.
        Supports cursor-based pagination and substring query filtering for high-asset accounts.
        """
        clean_token = (token or "").strip()
        if not clean_token:
            return {"success": False, "error": "Meta access token is required."}

        headers = {"Authorization": f"Bearer {clean_token}"}
        url = f"{self.BASE_URL}/me/accounts"
        fields = "id,name,category,access_token,tasks,instagram_business_account{id,username,name,profile_picture_url}"

        all_assets = []
        next_cursor = cursor
        pages_scanned = 0

        while pages_scanned < max_pages:
            params: Dict[str, Any] = {
                "fields": fields,
                "limit": min(limit_per_page, 100),
            }
            if next_cursor:
                params["after"] = next_cursor

            try:
                res = requests.get(url, params=params, headers=headers, timeout=20)
                if res.status_code != 200:
                    err = res.json().get("error", {})
                    return {
                        "success": False,
                        "status_code": res.status_code,
                        "error": err.get("message", res.text),
                    }

                data = res.json()
                items = data.get("data", [])
                for page in items:
                    ig_data = page.get("instagram_business_account")
                    asset_entry = {
                        "page_id": page.get("id"),
                        "page_name": page.get("name"),
                        "page_category": page.get("category"),
                        "page_access_token": page.get("access_token"),
                        "tasks": page.get("tasks", []),
                        "has_instagram": bool(ig_data),
                        "instagram": (
                            {
                                "id": ig_data.get("id"),
                                "username": ig_data.get("username"),
                                "name": ig_data.get("name"),
                                "profile_picture_url": ig_data.get("profile_picture_url"),
                            }
                            if ig_data
                            else None
                        ),
                    }
                    all_assets.append(asset_entry)

                paging = data.get("paging", {})
                cursors = paging.get("cursors", {})
                next_cursor = cursors.get("after")
                pages_scanned += 1

                # If no next page exists or no items were returned, stop
                if not next_cursor or not items or not paging.get("next"):
                    next_cursor = None
                    break

            except requests.RequestException as exc:
                return {"success": False, "error": f"Network exception fetching assets: {str(exc)}"}

        # Apply query filtering if provided (search across Page name or Instagram username)
        filtered_assets = all_assets
        if query and query.strip():
            q = query.strip().lower()
            filtered_assets = [
                a
                for a in all_assets
                if (q in a["page_name"].lower())
                or (a["instagram"] and q in (a["instagram"]["username"] or "").lower())
                or (a["instagram"] and q in (a["instagram"]["name"] or "").lower())
                or (q == str(a["page_id"]))
                or (a["instagram"] and q == str(a["instagram"]["id"]))
            ]

        return {
            "success": True,
            "total_fetched": len(all_assets),
            "total_matching": len(filtered_assets),
            "query": query,
            "pages_scanned": pages_scanned,
            "has_more": bool(next_cursor),
            "next_cursor": next_cursor,
            "assets": filtered_assets,
        }

    def update_channel_env(self, channel_slug: str, key_values: Dict[str, str]) -> Path:
        """
        Safely updates or appends environment variables in channels/<slug>/.env.
        Preserves all existing comments, blank lines, and non-target variables.
        Atomically commits changes and invalidates ChannelManager cache.
        """
        from src.core.channel_manager import ChannelManager, slugify_channel

        clean_slug = slugify_channel(channel_slug)
        channel_dir = self.root_dir / "channels" / clean_slug
        channel_dir.mkdir(parents=True, exist_ok=True)
        env_path = channel_dir / ".env"

        lines = []
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        # Track which keys from key_values were replaced in-place
        pending_keys = dict(key_values)
        updated_lines = []

        for line in lines:
            stripped = line.strip()
            # If line is a comment or blank, preserve as-is
            if not stripped or stripped.startswith("#"):
                updated_lines.append(line)
                continue

            # Check if this line is an assignment `KEY=...`
            match = re.match(r"^([A-Za-z_0-9]+)\s*=", stripped)
            if match:
                var_name = match.group(1)
                if var_name in pending_keys:
                    new_val = pending_keys.pop(var_name)
                    # Quote value safely if it contains spaces or symbols
                    updated_lines.append(f'{var_name}="{new_val}"\n')
                    continue

            updated_lines.append(line)

        # If any keys remain in pending_keys, append them under a Meta Suite section header
        if pending_keys:
            if updated_lines and not updated_lines[-1].endswith("\n"):
                updated_lines.append("\n")
            updated_lines.append("\n# === Meta Unified Publishing Suite (Direct Graph API) ===\n")
            for k, v in pending_keys.items():
                updated_lines.append(f'{k}="{v}"\n')

        # Atomic write
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile("w", dir=channel_dir, delete=False, encoding="utf-8") as tf:
                temp_file = tf.name
                tf.writelines(updated_lines)
                tf.flush()
                os.fsync(tf.fileno())
            os.replace(temp_file, env_path)
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass

        # Clear ChannelManager cache so new credentials take effect immediately
        ChannelManager().clear_cache()
        return env_path

    def bind_asset_to_channel(
        self,
        channel_slug: str,
        user_token: str,
        page_id: str,
        instagram_account_id: Optional[str] = None,
        page_access_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Binds a selected Facebook Page and/or Instagram account to an OmniPress channel.
        Resolves perpetual page tokens and live verifies access before writing to .env.
        """
        from src.core.channel_manager import ChannelManager, slugify_channel

        cm = ChannelManager(self.root_dir)
        clean_slug = slugify_channel(channel_slug)
        channel_info = cm.get_channel(clean_slug)

        if not channel_info:
            return {
                "success": False,
                "error": f"Channel '{clean_slug}' does not exist. Create the channel first via `omnipress_create_channel`.",
            }

        headers = {"Authorization": f"Bearer {user_token.strip()}"}
        page_url = f"{self.BASE_URL}/{page_id}"
        params = {
            "fields": "id,name,access_token,category,instagram_business_account{id,username,name}"
        }

        try:
            res = requests.get(page_url, params=params, headers=headers, timeout=15)
            if res.status_code != 200:
                err = res.json().get("error", {})
                return {
                    "success": False,
                    "error": f"Failed fetching page details for {page_id}: {err.get('message', res.text)}",
                }

            page_data = res.json()
            resolved_page_token = page_access_token or page_data.get("access_token") or user_token.strip()
            page_name = page_data.get("name", "")

            # Resolve Instagram Account
            ig_data = page_data.get("instagram_business_account")
            resolved_ig_id = instagram_account_id or (ig_data.get("id") if ig_data else "")
            resolved_ig_username = ig_data.get("username", "") if ig_data else ""

            # Prepare key-value dictionary to inject into channel .env
            env_updates: Dict[str, str] = {
                "FACEBOOK_PAGE_ID": str(page_id),
                "FACEBOOK_PAGE_NAME": page_name,
                "FACEBOOK_ACCESS_TOKEN": resolved_page_token,
            }

            if resolved_ig_id:
                env_updates["INSTAGRAM_ACCOUNT_ID"] = str(resolved_ig_id)
                env_updates["INSTAGRAM_ACCESS_TOKEN"] = resolved_page_token  # Page tokens also control linked IG!
                if resolved_ig_username:
                    env_updates["INSTAGRAM_USERNAME"] = resolved_ig_username

            env_path = self.update_channel_env(clean_slug, env_updates)

            return {
                "success": True,
                "channel_slug": clean_slug,
                "env_path": str(env_path),
                "facebook": {
                    "page_id": page_id,
                    "page_name": page_name,
                    "connected": True,
                },
                "instagram": {
                    "account_id": resolved_ig_id,
                    "username": resolved_ig_username,
                    "connected": bool(resolved_ig_id),
                },
            }

        except requests.RequestException as exc:
            return {"success": False, "error": f"Network exception during asset binding: {str(exc)}"}

    def get_oauth_login_url(
        self,
        app_id: str,
        redirect_uri: str = "http://localhost:8088/callback",
        scopes: Optional[List[str]] = None,
    ) -> str:
        """Generates the official Facebook OAuth 2.0 authorization dialog URL."""
        import urllib.parse

        default_scopes = [
            "pages_show_list",
            "pages_read_engagement",
            "pages_manage_posts",
            "instagram_basic",
            "instagram_content_publish",
        ]
        params = {
            "client_id": app_id.strip(),
            "redirect_uri": redirect_uri.strip(),
            "scope": ",".join(scopes or default_scopes),
            "response_type": "code",
        }
        return f"https://www.facebook.com/{self.GRAPH_API_VERSION}/dialog/oauth?{urllib.parse.urlencode(params)}"

    def exchange_code_for_token(
        self,
        code: str,
        app_id: str,
        app_secret: str,
        redirect_uri: str = "http://localhost:8088/callback",
    ) -> Dict[str, Any]:
        """
        Exchanges an OAuth code for a short-lived token, then immediately converts it
        into a 60-day Long-Lived User Access Token via Meta's fb_exchange_token grant.
        """
        clean_code = code.strip()
        url = f"{self.BASE_URL}/oauth/access_token"
        params = {
            "client_id": app_id.strip(),
            "client_secret": app_secret.strip(),
            "redirect_uri": redirect_uri.strip(),
            "code": clean_code,
        }
        try:
            res = requests.get(url, params=params, timeout=20)
            if res.status_code != 200:
                err = res.json().get("error", {})
                return {"success": False, "error": f"Failed exchanging code: {err.get('message', res.text)}"}

            short_token = res.json().get("access_token")
            if not short_token:
                return {"success": False, "error": "No access_token returned by Meta in code exchange."}

            long_params = {
                "grant_type": "fb_exchange_token",
                "client_id": app_id.strip(),
                "client_secret": app_secret.strip(),
                "fb_exchange_token": short_token,
            }
            long_res = requests.get(url, params=long_params, timeout=20)
            if long_res.status_code == 200:
                long_data = long_res.json()
                return {
                    "success": True,
                    "access_token": long_data.get("access_token", short_token),
                    "token_type": long_data.get("token_type", "bearer"),
                    "expires_in": long_data.get("expires_in"),
                    "is_long_lived": True,
                }

            return {
                "success": True,
                "access_token": short_token,
                "is_long_lived": False,
            }
        except requests.RequestException as exc:
            return {"success": False, "error": f"Network exception exchanging OAuth code: {str(exc)}"}

    def listen_for_oauth_callback(
        self,
        port: int = 8088,
        timeout_seconds: int = 180,
    ) -> Dict[str, Any]:
        """
        Starts a temporary HTTP server on localhost to listen for the Meta OAuth redirect.
        Captures the `code` or `error` query param, displays a clean confirmation page, and returns.
        """
        import http.server
        import urllib.parse
        import socketserver

        captured: Dict[str, Any] = {}

        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                if parsed.path == "/callback":
                    qs = urllib.parse.parse_qs(parsed.query)
                    code = qs.get("code", [None])[0]
                    error = qs.get("error_description", [qs.get("error", [None])[0]])[0]

                    if code:
                        captured["code"] = code
                        html = """
                        <!DOCTYPE html>
                        <html>
                        <head><title>OmniPress MCP — Autenticado</title><meta charset='utf-8'></head>
                        <body style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0A0D14; color: #F3F4F6; text-align: center; padding: 60px 20px;'>
                            <div style='max-width: 520px; margin: 0 auto; background: #111827; border: 1px solid #10B981; border-radius: 12px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.5);'>
                                <h1 style='color: #10B981; font-size: 28px; margin-bottom: 12px;'>✅ Login no Facebook Concluído!</h1>
                                <p style='color: #9CA3AF; font-size: 16px; line-height: 1.5;'>Suas permissões foram autorizadas com sucesso pelo OmniPress.</p>
                                <p style='color: #6EE7B7; font-weight: 600; margin-top: 24px;'>Você já pode fechar esta aba do navegador e voltar ao terminal.</p>
                            </div>
                        </body>
                        </html>
                        """
                        self.send_response(200)
                    else:
                        captured["error"] = error or "Nenhum código retornado pela Meta."
                        html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head><title>OmniPress MCP — Erro</title><meta charset='utf-8'></head>
                        <body style='font-family: sans-serif; background: #0A0D14; color: #F87171; text-align: center; padding: 60px;'>
                            <h1>❌ Falha na Autenticação</h1>
                            <p>{captured['error']}</p>
                        </body>
                        </html>
                        """
                        self.send_response(400)

                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(html.encode("utf-8"))
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                pass  # Silence standard HTTP access logs

        try:
            with socketserver.TCPServer(("localhost", port), CallbackHandler) as httpd:
                httpd.timeout = timeout_seconds
                httpd.handle_request()  # Handles exactly ONE request then shuts down
        except OSError as exc:
            return {"success": False, "error": f"Failed binding local server to port {port}: {str(exc)}"}

        if captured.get("code"):
            return {"success": True, "code": captured["code"]}
        return {"success": False, "error": captured.get("error", "Timeout waiting for Facebook OAuth callback.")}

