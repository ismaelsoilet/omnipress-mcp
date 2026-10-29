"""Stock asset provider: public-domain / open-license archive acquisition.

Uses an explicit allowlist of archives (Wikimedia Commons, Library of Congress,
US National Archives). Arbitrary domains and scraping are rejected.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

from src.engine.providers.base import ProviderError, RenderProvider, register

ALLOWED_DOMAINS = {
    "commons.wikimedia.org",
    "upload.wikimedia.org",
    "loc.gov",
    "www.loc.gov",
    "archives.gov",
    "www.archives.gov",
    "nara.gov",
}

DEFAULT_HEADERS = {
    "User-Agent": "OmniPressMCP/1.0 (public-domain asset acquisition; contact: repo owner)"
}


@register
class StockAssetProvider(RenderProvider):
    name = "stock_asset"
    capability = "network"
    supports = frozenset({"image", "asset"})
    default_extension = "jpg"

    def validate(self, spec: Dict[str, Any]) -> List[str]:
        errors = super().validate(spec)
        errors.extend(self.check_required(spec, ["query"]))
        for domain in spec.get("source_allowlist") or []:
            if domain not in ALLOWED_DOMAINS:
                errors.append(f"domain '{domain}' is not in the archive allowlist")
        return errors

    def _search_wikimedia(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        import requests

        response = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": f"filetype:bitmap {query}",
                "gsrnamespace": 6,
                "gsrlimit": limit,
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "iiurlwidth": 2400,
                "format": "json",
            },
            headers=DEFAULT_HEADERS,
            timeout=60,
        )
        response.raise_for_status()
        pages = (response.json().get("query") or {}).get("pages") or {}
        results = []
        for page in pages.values():
            infos = page.get("imageinfo") or []
            if not infos:
                continue
            info = infos[0]
            metadata = info.get("extmetadata") or {}
            results.append(
                {
                    "title": page.get("title", ""),
                    "url": info.get("thumburl") or info.get("url"),
                    "descriptionurl": info.get("descriptionurl"),
                    "license": (metadata.get("LicenseShortName") or {}).get("value", ""),
                    "artist": (metadata.get("Artist") or {}).get("value", ""),
                }
            )
        return results

    def render(self, spec: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
        errors = self.validate(spec)
        if errors:
            raise ProviderError("; ".join(errors))
        self._require(spec.get("channel_slug"))

        import requests

        allowlist = set(spec.get("source_allowlist") or ALLOWED_DOMAINS)
        results = self._search_wikimedia(str(spec["query"]), int(spec.get("limit", 3)))
        if not results:
            raise ProviderError(f"No archive results for query '{spec['query']}'.")

        chosen = None
        for candidate in results:
            host = urlparse(str(candidate.get("url") or "")).netloc.lower()
            if host in allowlist and host in ALLOWED_DOMAINS:
                chosen = candidate
                break
        if not chosen:
            raise ProviderError("Archive results did not contain an allowlisted asset URL.")

        output = self.resolve_output(out_dir, spec.get("output"), "asset")
        download = requests.get(chosen["url"], headers=DEFAULT_HEADERS, timeout=180)
        download.raise_for_status()
        output.write_bytes(download.content)

        manifest = {
            "status": "success",
            "provider": self.name,
            "output_path": str(output),
            "source_url": chosen.get("url"),
            "description_url": chosen.get("descriptionurl"),
            "title": chosen.get("title"),
            "license": spec.get("license") or chosen.get("license") or "unknown",
            "attribution": spec.get("attribution") or chosen.get("artist") or "",
            "file_size_bytes": output.stat().st_size,
        }
        manifest_path = Path(out_dir).resolve() / "asset_manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["manifest_path"] = str(manifest_path)
        return manifest
