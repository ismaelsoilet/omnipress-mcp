#!/usr/bin/env python3
"""OmniPress Media Upload Utility — Uploads media files using the configured storage provider (S3/R2/Catbox)."""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.storage import get_default_storage_provider


def main():
    provider = get_default_storage_provider()
    print(f"📦 Usando provedor de armazenamento: {provider.__class__.__name__}")

    target_files = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else [
        Path("media/assets/carrossel_02_slide1.jpg"),
        Path("media/assets/carrossel_02_slide2.jpg"),
    ]

    for f in target_files:
        if not f.exists():
            print(f"⚠️ Arquivo não encontrado: {f}")
            continue
        try:
            url = provider.upload_file(f)
            print(f"✅ {f.name} => {url}")
        except Exception as e:
            print(f"❌ Erro ao enviar {f.name}: {e}")


if __name__ == "__main__":
    main()
