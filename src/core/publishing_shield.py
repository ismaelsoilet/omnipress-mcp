import os
import tempfile
import hashlib
import json
import time
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

try:
    import fcntl
except ImportError:
    fcntl = None

_thread_lock = threading.RLock()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_LEDGER_PATH = PROJECT_ROOT / "media" / "staging" / "publishing_ledger.json"

# Strict character limits enforced by upstream social networks & Buffer
PLATFORM_CHAR_LIMITS = {
    "instagram": 2196,  # Buffer GraphQL strict cutoff
    "ig": 2196,
    "x": 280,
    "twitter": 280,
    "threads": 500,
    "linkedin": 3000,
}

PLACEHOLDER_TEST_TEXTS = {
    "teste",
    "test",
    "testing",
    "asdf",
    "asdfg",
    "foo",
    "bar",
    "hello world",
    "ola mundo",
    "post de teste",
    "teste 123",
}


class PublishingShield:
    """
    Guarantees zero accidental duplicate posts, enforces network character limits,
    and prevents dummy test text from hitting live production channels.
    """

    @staticmethod
    def get_ledger_path() -> Path:
        ledger = DEFAULT_LEDGER_PATH
        ledger.parent.mkdir(parents=True, exist_ok=True)
        return ledger

    @classmethod
    @contextmanager
    def _lock(cls, exclusive: bool = False):
        with _thread_lock:
            path = cls.get_ledger_path()
            lock_path = path.with_name(path.name + ".lock")
            f = None
            try:
                lock_path.parent.mkdir(parents=True, exist_ok=True)
                f = open(lock_path, "a+", encoding="utf-8")
                if fcntl:
                    mode = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
                    try:
                        fcntl.flock(f.fileno(), mode)
                    except OSError:
                        pass
                yield
            finally:
                if f:
                    if fcntl:
                        try:
                            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        except OSError:
                            pass
                    try:
                        f.close()
                    except Exception:
                        pass

    @classmethod
    def _load_ledger_unlocked(cls) -> List[Dict[str, Any]]:
        path = cls.get_ledger_path()
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    @classmethod
    def _save_ledger_unlocked(cls, entries: List[Dict[str, Any]]) -> None:
        path = cls.get_ledger_path()
        temp_name = None
        try:
            parent = path.parent
            parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", dir=parent, delete=False, encoding="utf-8") as tf:
                temp_name = tf.name
                json.dump(entries, tf, indent=2, ensure_ascii=False)
                tf.flush()
                os.fsync(tf.fileno())
            os.replace(temp_name, path)
        except Exception:
            if temp_name and os.path.exists(temp_name):
                try:
                    os.unlink(temp_name)
                except OSError:
                    pass

    @classmethod
    def load_ledger(cls) -> List[Dict[str, Any]]:
        with cls._lock(exclusive=False):
            return cls._load_ledger_unlocked()

    @classmethod
    def save_ledger(cls, entries: List[Dict[str, Any]]) -> None:
        with cls._lock(exclusive=True):
            cls._save_ledger_unlocked(entries)

    @staticmethod
    def generate_fingerprint(channel_id: str, text: str, media_urls: Optional[List[str]] = None) -> str:
        """Computes a deterministic SHA-256 fingerprint for a post on a specific channel."""
        normalized_text = " ".join(text.strip().lower().split())
        sorted_media = sorted(media_urls) if media_urls else []
        raw = f"{channel_id}|{normalized_text}|{','.join(sorted_media)}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def validate_post(
        cls,
        text: str,
        platforms: List[str],
        media_urls: Optional[List[str]] = None,
        mode: Optional[str] = None,
        allow_test: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """
        Runs comprehensive pre-flight validation gates before any network request is dispatched.
        Returns (is_valid, error_message).
        """
        normalized_platforms = [p.lower().strip() for p in platforms]
        text_clean = text.strip()

        # Gate 1: Dummy / Placeholder Test Interceptor
        if not allow_test and mode == "shareNow":
            lower_first_line = text_clean.split("\n")[0].lower().strip()
            if lower_first_line in PLACEHOLDER_TEST_TEXTS or len(text_clean) < 12:
                return (
                    False,
                    f"🛡️ Shield Block: Placeholder/test text '{text_clean[:30]}' cannot be dispatched to live production channels with shareNow (Rule 09). Use realistic content or run tests with local mocks.",
                )

        # Gate 2: Media Mandatory Check for Instagram
        is_instagram = any(p in ("instagram", "ig") for p in normalized_platforms)
        if is_instagram and (not media_urls or len(media_urls) == 0):
            return (
                False,
                "🛡️ Shield Block: Instagram strictly requires at least one media URL or public image endpoint. Text-only posting is not supported by Instagram.",
            )

        # Gate 3: Platform Character Limit Enforcement
        text_len = len(text)
        for plat in normalized_platforms:
            limit = PLATFORM_CHAR_LIMITS.get(plat)
            if limit and text_len > limit:
                excess = text_len - limit
                return (
                    False,
                    f"🛡️ Shield Block: Caption exceeds maximum allowed length for {plat.upper()}: {text_len} characters (limit: {limit}). Please shorten text by {excess} character(s) before dispatching.",
                )

        return True, None

    @classmethod
    def _resolve_channel_aliases(cls, channel_id: str) -> set:
        """Resolves known aliases for a channel ID (e.g. channel_slug <-> buffer_channel_id)."""
        aliases = {channel_id}
        try:
            from src.core.channel_manager import ChannelManager
            cm = ChannelManager()
            ch = cm.get_channel(channel_id)
            if ch:
                for s_info in ch.get("social", {}).values():
                    if isinstance(s_info, dict) and s_info.get("buffer_channel_id"):
                        aliases.add(s_info["buffer_channel_id"])
            else:
                for ch_item in cm.list_channels(include_templates=False):
                    slug = ch_item.get("slug")
                    for s_info in ch_item.get("social", {}).values():
                        if isinstance(s_info, dict) and s_info.get("buffer_channel_id") == channel_id:
                            if slug:
                                aliases.add(slug)
        except Exception:
            pass
        return aliases

    @classmethod
    def check_duplicate(
        cls,
        channel_id: str,
        text: str,
        media_urls: Optional[List[str]] = None,
        window_seconds: int = 86400,  # 24 hours default
        force: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifies if an identical post was already dispatched to this channel in the given window.
        Inspects channel aliases (e.g. buffer_channel_id and channel_slug) to prevent cross-layer duplicates.
        Returns (is_duplicate, error_message).
        """
        if force:
            return False, None

        aliases = cls._resolve_channel_aliases(channel_id)
        now = time.time()
        ledger = cls.load_ledger()

        for candidate_id in aliases:
            fingerprint = cls.generate_fingerprint(candidate_id, text, media_urls)
            for entry in ledger:
                if entry.get("fingerprint") == fingerprint:
                    elapsed = now - entry.get("timestamp", 0)
                    if elapsed < window_seconds:
                        hours_ago = round(elapsed / 3600, 1)
                        return (
                            True,
                            f"🛡️ Shield Block (Rule 09 Exactly-Once): This exact post was already published to channel '{candidate_id}' {hours_ago}h ago (Post ID: {entry.get('post_id', 'unknown')}). Duplicate dispatch blocked to protect account reputation.",
                        )

        return False, None

    @classmethod
    def record_published(
        cls,
        channel_id: str = "",
        text: str = "",
        media_urls: Optional[List[str]] = None,
        post_id: Optional[str] = None,
        provider: str = "buffer_graphql",
        **kwargs: Any,
    ) -> None:
        """Records a successful publication in the persistent idempotency ledger.
        
        Supports flexible kwargs (status, response, channel_slug, etc.) for cross-engine compatibility.
        """
        if not channel_id and "channel_slug" in kwargs:
            channel_id = str(kwargs.pop("channel_slug"))

        fingerprint = cls.generate_fingerprint(channel_id, text, media_urls)
        with cls._lock(exclusive=True):
            ledger = cls._load_ledger_unlocked()

            # Purge entries older than 7 days to keep file light
            cutoff = time.time() - (7 * 86400)
            clean_ledger = [e for e in ledger if e.get("timestamp", 0) > cutoff and e.get("fingerprint") != fingerprint]

            entry: Dict[str, Any] = {
                "fingerprint": fingerprint,
                "channel_id": channel_id,
                "post_id": post_id,
                "provider": provider,
                "timestamp": time.time(),
                "text_preview": text[:80].replace("\n", " "),
                "media_count": len(media_urls) if media_urls else 0,
            }
            if "status" in kwargs:
                entry["status"] = str(kwargs["status"])

            clean_ledger.append(entry)
            cls._save_ledger_unlocked(clean_ledger)

    @classmethod
    def remove_entry(cls, post_id: str) -> None:
        """Removes an entry from the ledger if a post is deleted via delete_post."""
        with cls._lock(exclusive=True):
            ledger = cls._load_ledger_unlocked()
            updated = [e for e in ledger if e.get("post_id") != post_id]
            if len(updated) != len(ledger):
                cls._save_ledger_unlocked(updated)
