"""OmniPress Storage Manager — Agnostic file and asset hosting for social platforms (Instagram, etc.)."""

import os
import time
import urllib.request
import urllib.parse
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class BaseStorageProvider(ABC):
    """Abstract interface for media asset storage providers."""

    @abstractmethod
    def upload_file(self, file_path: Path, remote_name: Optional[str] = None) -> str:
        """Uploads a local media file and returns a publicly accessible HTTPS URL."""
        pass


class CatboxStorageProvider(BaseStorageProvider):
    """
    Catbox.moe ephemeral upload provider.
    Used as development fallback when no dedicated S3/R2 object storage is configured.
    """

    API_URL = "https://catbox.moe/user/api.php"

    def upload_file(self, file_path: Path, remote_name: Optional[str] = None) -> str:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Media file not found: {file_path}")

        boundary = "----OmniPressStorageBoundary"
        data = bytearray()
        data.extend(f"--{boundary}\r\n".encode())
        data.extend(b'Content-Disposition: form-data; name="reqtype"\r\n\r\n')
        data.extend(b"fileupload\r\n")

        filename = remote_name or file_path.name
        import mimetypes
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        data.extend(f"--{boundary}\r\n".encode())
        data.extend(f'Content-Disposition: form-data; name="fileToUpload"; filename="{filename}"\r\n'.encode())
        data.extend(f"Content-Type: {content_type}\r\n\r\n".encode())
        data.extend(file_path.read_bytes())
        data.extend(b"\r\n")
        data.extend(f"--{boundary}--\r\n".encode())

        req = urllib.request.Request(
            self.API_URL,
            data=bytes(data),
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": "OmniPress-MCP/1.0",
            },
        )

        last_error = None
        for attempt in range(1, 4):
            try:
                with urllib.request.urlopen(req, timeout=45) as resp:
                    url = resp.read().decode("utf-8").strip()
                    if url.startswith("http://") or url.startswith("https://"):
                        return url
                    raise RuntimeError(f"Storage upload returned invalid response: {url[:100]}")
            except Exception as e:
                last_error = e
                if attempt < 3:
                    time.sleep(attempt * 1.5)

        raise RuntimeError(f"Catbox upload failed after 3 attempts: {last_error}")


class LocalStaticStorageProvider(BaseStorageProvider):
    """
    Local web-server storage provider.
    Serves files from media/staging/ via the application container's public URL.
    """

    def __init__(self, public_base_url: str, staging_dir: Optional[Path] = None):
        self.public_base_url = public_base_url.rstrip("/")
        if staging_dir:
            self.staging_dir = Path(staging_dir).resolve()
        else:
            default_dir = PROJECT_ROOT / "media" / "staging"
            self.staging_dir = Path(os.getenv("MEDIA_STAGING_DIR", str(default_dir))).resolve()
        self.staging_dir.mkdir(parents=True, exist_ok=True)

    def upload_file(self, file_path: Path, remote_name: Optional[str] = None) -> str:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"Media file not found: {file_path}")

        filename = Path(remote_name or file_path.name).name
        dest_path = self.staging_dir / filename
        if file_path != dest_path.resolve():
            shutil.copy2(file_path, dest_path)

        return f"{self.public_base_url}/media/staging/{filename}"


class S3StorageProvider(BaseStorageProvider):
    """
    S3 / Cloudflare R2 / MinIO compatible object storage provider.
    """

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: Optional[str] = None,
        public_url_prefix: Optional[str] = None,
    ):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.public_url_prefix = public_url_prefix.rstrip("/") if public_url_prefix else None

    def upload_file(self, file_path: Path, remote_name: Optional[str] = None) -> str:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Media file not found: {file_path}")

        key = Path(remote_name or file_path.name).name
        try:
            import boto3  # Optional dependency
            import mimetypes
            s3 = boto3.client("s3", endpoint_url=self.endpoint_url)
            content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
            extra_args: Dict[str, Any] = {"ContentType": content_type}
            s3_acl = os.getenv("S3_ACL")
            if s3_acl:
                extra_args["ACL"] = s3_acl

            s3.upload_file(
                str(file_path),
                self.bucket_name,
                key,
                ExtraArgs=extra_args,
            )
            if self.public_url_prefix:
                return f"{self.public_url_prefix}/{key}"
            if self.endpoint_url:
                return f"{self.endpoint_url.rstrip('/')}/{self.bucket_name}/{key}"
            return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
        except ImportError:
            raise RuntimeError("boto3 is required for S3StorageProvider. Install via 'uv add boto3'")


def get_default_storage_provider(channel_slug: Optional[str] = None) -> BaseStorageProvider:
    """
    Resolves the active storage provider with Rule 04 channel precedence:
    1. S3 / R2 / MinIO (if S3_BUCKET_NAME / R2_BUCKET_NAME is set in channel or global env)
    2. Local static server (if OMNIPRESS_PUBLIC_URL is set in channel or global env)
    3. Catbox fallback
    """
    try:
        from src.core.channel_manager import ChannelManager
        cm = ChannelManager()
        s3_bucket = cm.get_credential("S3_BUCKET_NAME", channel_slug) or cm.get_credential("R2_BUCKET_NAME", channel_slug)
        if s3_bucket:
            endpoint = cm.get_credential("S3_ENDPOINT_URL", channel_slug) or cm.get_credential("R2_ENDPOINT_URL", channel_slug)
            prefix = cm.get_credential("S3_PUBLIC_URL_PREFIX", channel_slug) or cm.get_credential("R2_PUBLIC_URL_PREFIX", channel_slug)
            return S3StorageProvider(s3_bucket, endpoint_url=endpoint or None, public_url_prefix=prefix or None)

        public_url = cm.get_credential("OMNIPRESS_PUBLIC_URL", channel_slug)
        if public_url:
            return LocalStaticStorageProvider(public_url)
    except Exception:
        pass

    s3_bucket = os.getenv("S3_BUCKET_NAME") or os.getenv("R2_BUCKET_NAME")
    if s3_bucket:
        endpoint = os.getenv("S3_ENDPOINT_URL") or os.getenv("R2_ENDPOINT_URL")
        prefix = os.getenv("S3_PUBLIC_URL_PREFIX") or os.getenv("R2_PUBLIC_URL_PREFIX")
        return S3StorageProvider(s3_bucket, endpoint_url=endpoint, public_url_prefix=prefix)

    public_url = os.getenv("OMNIPRESS_PUBLIC_URL")
    if public_url:
        return LocalStaticStorageProvider(public_url)

    return CatboxStorageProvider()
