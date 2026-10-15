"""Global Pytest fixtures for OmniPress test suite.

Ensures complete test isolation, mock ledgers, and zero side effects on production staging files.
"""

import pytest
from src.core.publishing_shield import PublishingShield


@pytest.fixture(autouse=True)
def isolate_publishing_ledger(tmp_path, monkeypatch):
    """
    Automatically isolates the PublishingShield idempotency ledger for every unit test.
    Prevents tests from colliding with each other or with media/staging/publishing_ledger.json.
    """
    test_ledger = tmp_path / "test_isolated_ledger.json"
    monkeypatch.setattr(PublishingShield, "get_ledger_path", classmethod(lambda cls: test_ledger))
    yield test_ledger
