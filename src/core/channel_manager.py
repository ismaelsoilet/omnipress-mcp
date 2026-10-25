"""OmniPress Channel Manager - Multi-tenant channel management engine."""

import os
import json
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def slugify_channel(value: str) -> str:
    """Converts a name or handle into a filesystem-safe slug."""
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s_]+", "-", value).strip("-")


class ChannelManager:
    """
    Manages channel workspaces in OmniPress.
    Provides discovery, loading, creation, and path resolution for multiple distinct publishing channels.
    """

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = Path(root_dir or PROJECT_ROOT).resolve()
        self.channels_dir = self.root_dir / "channels"
        self.channels_dir.mkdir(parents=True, exist_ok=True)

    def list_channels(self, include_templates: bool = False) -> List[Dict[str, Any]]:
        """Discovers all configured channels with valid channel.json files."""
        channels = []
        if not self.channels_dir.exists():
            return channels

        for item in sorted(self.channels_dir.iterdir()):
            if not item.is_dir():
                continue
            if item.name.startswith("_") and not include_templates:
                continue

            config_file = item / "channel.json"
            if config_file.exists():
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        data["path"] = str(item)
                        channels.append(data)
                except Exception as e:
                    channels.append({
                        "slug": item.name,
                        "name": item.name,
                        "path": str(item),
                        "error": str(e)
                    })
        return channels

    def get_channel(self, slug: str) -> Optional[Dict[str, Any]]:
        """Returns the configuration for a specific channel slug."""
        clean_slug = slugify_channel(slug)
        target_dir = self.channels_dir / clean_slug
        config_file = target_dir / "channel.json"

        if not config_file.exists():
            return None

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["path"] = str(target_dir)
                return data
        except Exception:
            return None

    def get_active_channel_slug(self) -> str:
        """Determines the active channel based on environment, default, or fallback."""
        env_raw = os.getenv("OMNIPRESS_ACTIVE_CHANNEL", "").strip()
        env_channel = slugify_channel(env_raw) if env_raw else ""
        if env_channel and env_channel != "_template" and (self.channels_dir / env_channel).exists():
            return env_channel

        channels = self.list_channels(include_templates=False)
        if channels:
            return channels[0].get("slug", "default")

        return "default"

    def get_active_channel(self) -> Dict[str, Any]:
        """Returns the active channel configuration."""
        slug = self.get_active_channel_slug()
        channel = self.get_channel(slug)
        if channel:
            return channel

        # Fallback default dict
        return {
            "slug": slug,
            "name": slug.replace("-", " ").title(),
            "branding": {
                "handle": f"@{slug}",
                "badge_text": "OMNIPRESS",
                "theme_colors": {"primary": "#D4AF37", "background": "#0A0C10", "text": "#FFFFFF"},
                "typography": {
                    "bold_font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "regular_font": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                }
            },
            "video": {
                "aspect_ratio": "16:9",
                "soundtrack_volume": 0.16,
            },
            "path": str(self.channels_dir / slug)
        }

    def get_channel_dir(self, slug: Optional[str] = None) -> Path:
        """Resolves the root directory of a channel."""
        target_slug = slugify_channel(slug) if slug else self.get_active_channel_slug()
        c_dir = self.channels_dir / target_slug
        c_dir.mkdir(parents=True, exist_ok=True)
        return c_dir

    def get_channel_env(self, slug: Optional[str] = None) -> Dict[str, str]:
        """Loads and returns environment variables defined in channels/<slug>/.env if present."""
        target_slug = slugify_channel(slug) if slug else self.get_active_channel_slug()
        env_file = self.channels_dir / target_slug / ".env"
        if not env_file.exists():
            return {}
        try:
            from dotenv import dotenv_values
            return {str(k): str(v) for k, v in dotenv_values(env_file).items() if v is not None}
        except Exception:
            return {}

    def get_articles_dir(self, slug: Optional[str] = None) -> Path:
        """Returns the articles directory for a channel."""
        art_dir = self.get_channel_dir(slug) / "articles"
        art_dir.mkdir(parents=True, exist_ok=True)
        return art_dir

    def get_media_dir(self, slug: Optional[str] = None, subfolder: str = "") -> Path:
        """Returns the media directory (or subfolder) for a channel."""
        m_dir = self.get_channel_dir(slug) / "media"
        if subfolder:
            clean_subfolder = Path(subfolder).name
            m_dir = m_dir / clean_subfolder
        m_dir.mkdir(parents=True, exist_ok=True)
        return m_dir

    def get_scripts_dir(self, slug: Optional[str] = None) -> Path:
        """Returns the channel-specific custom scripts directory."""
        s_dir = self.get_channel_dir(slug) / "scripts"
        s_dir.mkdir(parents=True, exist_ok=True)
        return s_dir

    def create_channel(
        self,
        slug: str,
        name: str,
        handle: str,
        category: str = "general",
        description: str = "",
        primary_color: str = "#D4AF37",
        buffer_channel_id: str = "",
        default_hashtags: Optional[List[str]] = None,
        archetype: str = "personal_brand",
    ) -> Dict[str, Any]:
        """
        Scaffolds a new, isolated channel workspace with folders and channel.json.
        Supports both personal brand profiles and media channels.
        """
        clean_slug = slugify_channel(slug)
        channel_dir = self.channels_dir / clean_slug
        channel_dir.mkdir(parents=True, exist_ok=True)

        is_media = archetype in ("media_channel", "media_house", "hybrid")

        # Create structured subdirectories per Rule 04 & Rule 10
        (channel_dir / "articles").mkdir(parents=True, exist_ok=True)
        (channel_dir / "campanhas").mkdir(parents=True, exist_ok=True)
        (channel_dir / "media" / "raw").mkdir(parents=True, exist_ok=True)
        (channel_dir / "media" / "carousels").mkdir(parents=True, exist_ok=True)
        (channel_dir / "media" / "stories").mkdir(parents=True, exist_ok=True)
        (channel_dir / "media" / "highlights").mkdir(parents=True, exist_ok=True)
        (channel_dir / "media" / "visuals").mkdir(parents=True, exist_ok=True)
        (channel_dir / "media" / "voiceover").mkdir(parents=True, exist_ok=True)
        (channel_dir / "media" / "soundtrack").mkdir(parents=True, exist_ok=True)
        (channel_dir / "media" / "output").mkdir(parents=True, exist_ok=True)
        if is_media:
            (channel_dir / "episodios").mkdir(parents=True, exist_ok=True)
            (channel_dir / "documentarios").mkdir(parents=True, exist_ok=True)
            (channel_dir / "shorts").mkdir(parents=True, exist_ok=True)
        (channel_dir / "scripts").mkdir(parents=True, exist_ok=True)

        config: Dict[str, Any] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "id": clean_slug,
            "name": name,
            "slug": clean_slug,
            "archetype": archetype,
            "description": description or f"Canal de conteúdo {name}.",
            "category": category,
            "features": {
                "articles": True,
                "carousels": True,
                "social_posts": True,
                "video": is_media,
            },
            "branding": {
                "handle": handle if handle.startswith("@") else f"@{handle}",
                "badge_text": name.upper(),
                "theme_colors": {
                    "primary": primary_color,
                    "background": "#0A0C10",
                    "text": "#FFFFFF",
                    "secondary_text": "#E1E6EB"
                },
                "typography": {
                    "bold_font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "regular_font": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                }
            },
            "visual_identity": {
                "default_preset": "tweet_card" if archetype == "personal_brand" else "classic_card",
                "palette": {
                    "primary": primary_color,
                    "background": "#FFFFFF" if archetype == "personal_brand" else "#0A0C10",
                    "card_background": "#F8FAFC" if archetype == "personal_brand" else "#080A0E",
                    "text": "#0F172A" if archetype == "personal_brand" else "#FFFFFF",
                    "secondary_text": "#64748B" if archetype == "personal_brand" else "#E1E6EB",
                    "accent": primary_color,
                    "border": "#E2E8F0" if archetype == "personal_brand" else primary_color,
                },
                "typography": {
                    "font_family": "sans" if archetype == "personal_brand" else "serif",
                    "bold_font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "regular_font": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "serif_bold_font": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                    "serif_regular_font": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                    "mono_font": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                },
                "author": {
                    "name": name,
                    "handle": handle if handle.startswith("@") else f"@{handle}",
                    "title": description or name,
                    "avatar_path": "media/raw/avatar.jpg",
                    "verified": archetype == "personal_brand",
                },
                "elements": {
                    "bullet_style": "square",
                    "watermark_text": name.upper(),
                    "enable_shadow": True,
                },
            },
            "social": {
                "linkedin": {
                    "handle": handle.replace("@", ""),
                    "profile_id": "",
                    "buffer_channel_id": ""
                },
                "x_twitter": {
                    "handle": handle.replace("@", ""),
                    "buffer_channel_id": ""
                },
                "instagram": {
                    "handle": handle.replace("@", ""),
                    "buffer_channel_id": buffer_channel_id,
                    "default_hashtags": default_hashtags or [f"#{clean_slug.replace('-', '')}", "#conteudo"]
                },
                "threads": {
                    "handle": handle.replace("@", ""),
                    "buffer_channel_id": ""
                },
                "youtube": {
                    "channel_id": "",
                    "buffer_channel_id": "",
                    "default_privacy": "public"
                }
            },
            "video": {
                "enabled": is_media,
                "aspect_ratio": "16:9",
                "soundtrack_volume": 0.16,
                "fps": 30,
            },
            "settings": {
                "auto_sanitize": True,
                "default_aspect_ratio": "4:5" if archetype == "personal_brand" else "3:4"
            }
        }

        config_path = channel_dir / "channel.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # Automatically generate channel style_guide.md
        style_guide_path = channel_dir / "style_guide.md"
        if not style_guide_path.exists():
            template_sg = self.channels_dir / "_template" / "style_guide.md"
            if template_sg.exists():
                sg_content = template_sg.read_text(encoding="utf-8")
                sg_content = sg_content.replace("@seuperfil", handle if handle.startswith("@") else f"@{handle}")
                sg_content = sg_content.replace("Nome Oficial ou Marca", name)
                style_guide_path.write_text(sg_content, encoding="utf-8")

        # Automatically scaffold channel-specific .env for isolated credentials (Rule 04)
        env_example_path = channel_dir / ".env.example"
        env_template = (
            f"# ==============================================================================\n"
            f"# OmniPress MCP — Channel Environment Secrets: {clean_slug}\n"
            f"# ==============================================================================\n"
            f"# Personal Buffer API Key (https://publish.buffer.com/settings/api)\n"
            f"BUFFER_API_KEY=\n\n"
            f"# Optional overrides for channel profile IDs (auto-discovered if empty)\n"
            f"BUFFER_LINKEDIN_PROFILE_ID=\n"
            f"BUFFER_X_PROFILE_ID=\n"
            f"BUFFER_INSTAGRAM_PROFILE_ID={buffer_channel_id}\n"
            f"BUFFER_THREADS_PROFILE_ID=\n"
        )
        if not env_example_path.exists():
            env_example_path.write_text(env_template, encoding="utf-8")

        env_path = channel_dir / ".env"
        if not env_path.exists():
            env_path.write_text(env_template, encoding="utf-8")

        # Copy campaign template into campanhas/ if available
        src_camp = self.channels_dir / "_template" / "campanhas" / "_template_campanha"
        dst_camp = channel_dir / "campanhas" / "_template_campanha"
        if src_camp.exists() and not dst_camp.exists():
            import shutil
            shutil.copytree(src_camp, dst_camp)

        config["path"] = str(channel_dir)
        return config
