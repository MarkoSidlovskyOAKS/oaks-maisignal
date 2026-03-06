"""Shared fixtures for MAiSIGNAL backend tests."""

import pytest

from maisignal.domain.models import Recipient


@pytest.fixture()
def sample_html():
    """Minimal HTML content for testing."""
    return "<html><body><h1>Test Alert</h1></body></html>"


@pytest.fixture()
def sample_api_key():
    """Fake API key for testing."""
    return "test-api-key-12345"


@pytest.fixture()
def sample_recipient():
    """Sample Recipient for testing."""
    return Recipient(email="test@example.com", name="Test User")


@pytest.fixture()
def sample_payload(sample_html, sample_recipient):
    """Pre-built payload for testing."""
    from maisignal.domain.alert_service import build_payload

    return build_payload(sample_html, sample_recipient)
