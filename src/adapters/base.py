"""Base abstract interface for OmniPress publishing adapters."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BasePublisherAdapter(ABC):
    """Abstract base class for all OmniPress content distribution adapters."""

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the required credentials/settings are present."""
        pass

    @abstractmethod
    def queue_social_post(
        self,
        text: str,
        platforms: List[str],
        media_urls: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Queues or publishes a short-form social post to target networks.
        """
        pass
