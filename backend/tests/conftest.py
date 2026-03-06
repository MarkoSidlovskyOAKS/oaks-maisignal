"""Shared fixtures for MAiSIGNAL backend tests."""

import pytest


@pytest.fixture()
def sample_html():
    """Minimal HTML content for testing."""
    return "<html><body><h1>Test Alert</h1></body></html>"


@pytest.fixture()
def sample_api_key():
    """Fake API key for testing."""
    return "test-api-key-12345"


@pytest.fixture()
def sample_payload(sample_html):
    """Pre-built payload for testing."""
    from send_maisignal_alert import build_payload

    return build_payload(sample_html)
