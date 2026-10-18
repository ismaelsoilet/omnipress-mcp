"""Dedicated unit tests for OmniPress storage provider abstraction (src/utils/storage.py)."""

import io
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from src.utils.storage import (
    BaseStorageProvider,
    CatboxStorageProvider,
    LocalStaticStorageProvider,
    S3StorageProvider,
    get_default_storage_provider,
)


def test_local_static_storage_provider(tmp_path: Path):
    """Verify local container web-server storage generates expected public URLs."""
    staging_dir = tmp_path / "staging"
    provider = LocalStaticStorageProvider("https://omnipress.suitplus.com.br/", staging_dir=staging_dir)
    assert provider.public_base_url == "https://omnipress.suitplus.com.br"

    sample_file = tmp_path / "slide_01.jpg"
    sample_file.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF")

    # Standard upload
    url = provider.upload_file(sample_file)
    assert url == "https://omnipress.suitplus.com.br/media/staging/slide_01.jpg"
    assert (provider.staging_dir / "slide_01.jpg").exists()

    # Custom remote name
    url_custom = provider.upload_file(sample_file, remote_name="custom_hero.jpg")
    assert url_custom == "https://omnipress.suitplus.com.br/media/staging/custom_hero.jpg"
    assert (provider.staging_dir / "custom_hero.jpg").exists()

    # Missing file raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        provider.upload_file(tmp_path / "non_existent.jpg")


def test_catbox_storage_provider(tmp_path: Path):
    """Verify Catbox.moe multipart upload payload formatting and response parsing."""
    provider = CatboxStorageProvider()
    sample_file = tmp_path / "photo.png"
    sample_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")

    fake_response = io.BytesIO(b"https://files.catbox.moe/abc123xyz.png\n")

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = fake_response

        url = provider.upload_file(sample_file)
        assert url == "https://files.catbox.moe/abc123xyz.png"
        assert mock_urlopen.called

        req_arg = mock_urlopen.call_args[0][0]
        assert req_arg.full_url == "https://catbox.moe/user/api.php"
        assert "multipart/form-data" in req_arg.headers["Content-type"]

    # Missing file raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        provider.upload_file(tmp_path / "missing.png")


def test_s3_storage_provider_with_mocked_boto3(tmp_path: Path):
    """Verify S3/R2 upload parameters, ACL, content-type and custom URL prefix."""
    sample_file = tmp_path / "graphic.jpg"
    sample_file.write_bytes(b"\xFF\xD8\xFF\xE0")

    mock_boto3 = MagicMock()
    mock_s3_client = MagicMock()
    mock_boto3.client.return_value = mock_s3_client

    with patch.dict("sys.modules", {"boto3": mock_boto3}):
        # Test AWS S3 standard URL (ACL omitted by default for modern AWS / R2 bucket owner enforced)
        provider = S3StorageProvider(bucket_name="my-bucket")
        url = provider.upload_file(sample_file)
        assert url == "https://my-bucket.s3.amazonaws.com/graphic.jpg"
        mock_s3_client.upload_file.assert_called_with(
            str(sample_file),
            "my-bucket",
            "graphic.jpg",
            ExtraArgs={"ContentType": "image/jpeg"},
        )

        # Test with S3_ACL env override
        with patch.dict("os.environ", {"S3_ACL": "public-read"}):
            provider.upload_file(sample_file)
            mock_s3_client.upload_file.assert_called_with(
                str(sample_file),
                "my-bucket",
                "graphic.jpg",
                ExtraArgs={"ContentType": "image/jpeg", "ACL": "public-read"},
            )

        # Test Cloudflare R2 / Custom CDN prefix
        r2_provider = S3StorageProvider(
            bucket_name="r2-bucket",
            endpoint_url="https://account.r2.cloudflarestorage.com",
            public_url_prefix="https://media.mybrand.dev",
        )
        r2_url = r2_provider.upload_file(sample_file, remote_name="renamed.jpg")
        assert r2_url == "https://media.mybrand.dev/renamed.jpg"


def test_s3_storage_provider_missing_boto3(tmp_path: Path):
    """Verify informative RuntimeError when boto3 is not installed."""
    sample_file = tmp_path / "asset.png"
    sample_file.write_bytes(b"\x89PNG")

    provider = S3StorageProvider(bucket_name="test-bucket")
    with patch.dict("sys.modules", {"boto3": None}):
        with pytest.raises(RuntimeError) as exc_info:
            provider.upload_file(sample_file)
        assert "boto3 is required" in str(exc_info.value)


def test_storage_provider_hierarchy_resolution(monkeypatch):
    """Verify resolution priority: S3/R2 -> Local Static -> Catbox fallback."""
    # Clear storage env vars
    for var in [
        "S3_BUCKET_NAME",
        "R2_BUCKET_NAME",
        "S3_ENDPOINT_URL",
        "S3_PUBLIC_URL_PREFIX",
        "OMNIPRESS_PUBLIC_URL",
    ]:
        monkeypatch.delenv(var, raising=False)

    # 1. Fallback to Catbox
    p_fallback = get_default_storage_provider()
    assert isinstance(p_fallback, CatboxStorageProvider)

    # 2. Local container hosting
    monkeypatch.setenv("OMNIPRESS_PUBLIC_URL", "https://omnipress.local")
    p_local = get_default_storage_provider()
    assert isinstance(p_local, LocalStaticStorageProvider)

    # 3. S3 / R2 takes highest precedence
    monkeypatch.setenv("S3_BUCKET_NAME", "brand-assets")
    p_s3 = get_default_storage_provider()
    assert isinstance(p_s3, S3StorageProvider)
    assert p_s3.bucket_name == "brand-assets"

    # Cloudflare R2 alias
    monkeypatch.delenv("S3_BUCKET_NAME")
    monkeypatch.setenv("R2_BUCKET_NAME", "cloudflare-r2-assets")
    p_r2 = get_default_storage_provider()
    assert isinstance(p_r2, S3StorageProvider)
    assert p_r2.bucket_name == "cloudflare-r2-assets"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
