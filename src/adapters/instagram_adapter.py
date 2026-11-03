"""Direct Meta Instagram Graph API publishing adapter for OmniPress.

Re-exports MetaPublisherAdapter for backward-compatibility while enabling
the full Meta Suite (Instagram Reels, Facebook Pages, Threads, First-Comment).
"""

from .meta_adapter import (
    MetaPublisherAdapter,
    MetaGraphAdapter,
    InstagramGraphAdapter,
)

__all__ = [
    "MetaPublisherAdapter",
    "MetaGraphAdapter",
    "InstagramGraphAdapter",
]
