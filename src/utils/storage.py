"""OmniPress Storage Manager — Agnostic file and asset hosting for social platforms (Instagram, etc.)."""

import os
import urllib.request
import urllib.parse
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


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
        content_type = "image/png" if file_path.suffix.lower() == ".png" else "image/jpeg"
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

        with urllib.request.urlopen(req, timeout=45) as resp:
            return resp.read().decode("utf-8").strip()


class LocalStaticStorageProvider(BaseStorageProvider):
    """
    Local web-server storage provider.
    Serves files from media/staging/ via the application container's public URL.
    """

    def __init__(self, public_base_url: str):
        self.public_base_url = public_base_url.rstrip("/")

    def upload_file(self, file_path: Path, remote_name: Optional[str] = None) -> str:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Media file not found: {file_path}")

        filename = remote_name or file_path.name
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

        key = remote_name or file_path.name
        try:
            import boto3  # Optional dependency
            s3 = boto3.client("s3", endpoint_url=self.endpoint_url)
            content_type = "image/png" if file_path.suffix.lower() == ".png" else "image/jpeg"
            s3.upload_file(
                str(file_path),
                self.bucket_name,
                key,
                ExtraArgs={"ContentType": content_type, "ACL": "public-read"},
            )
            if self.public_url_prefix:
                return f"{self.public_url_prefix}/{key}"
            return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
        except ImportError:
            raise RuntimeError("boto3 is required for S3StorageProvider. Install via 'uv add boto3'")


def get_default_storage_provider() -> BaseStorageProvider:
    """
    Resolves the active storage provider from environment variables.
    Priority:
    1. S3 / R2 / MinIO (if S3_BUCKET_NAME is set)
    2. Local static server (if OMNIPRESS_PUBLIC_URL is set)
    3. Catbox fallback
    """
    s3_bucket = os.getenv("S3_BUCKET_NAME") or os.getenv("R2_BUCKET_NAME")
    if s3_bucket:
        endpoint = os.getenv("S3_ENDPOINT_URL") or os.getenv("R2_ENDPOINT_URL")
        prefix = os.getenv("S3_PUBLIC_URL_PREFIX") or os.getenv("R2_PUBLIC_URL_PREFIX")
        return S3StorageProvider(s3_bucket, endpoint_url=endpoint, public_url_prefix=prefix)

    public_url = os.getenv("OMNIPRESS_PUBLIC_URL")
    if public_url:
        return LocalStaticStorageProvider(public_url)

    return CatboxStorageProvider()
