"""Tests for MAiSIGNAL infrastructure adapters."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from maisignal.adapters.ecomail_sender import EcomailSender
from maisignal.adapters.file_template_loader import FileTemplateLoader
from maisignal.adapters.snowflake_repository import SnowflakeRecipientRepository
from maisignal.domain.models import Recipient

# ── SnowflakeRecipientRepository ─────────────────────────────────────


class TestSnowflakeRecipientRepository:
    @patch("maisignal.adapters.snowflake_repository.snowflake.connector.connect")
    def test_returns_recipients(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("a@example.com", "Company A"),
            ("b@example.com", "Company B"),
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        repo = SnowflakeRecipientRepository({"account": "acct"})
        result = repo.get_all()

        assert result == [
            Recipient(email="a@example.com", name="Company A"),
            Recipient(email="b@example.com", name="Company B"),
        ]
        mock_conn.close.assert_called_once()

    @patch("maisignal.adapters.snowflake_repository.snowflake.connector.connect")
    def test_empty_result_raises(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        repo = SnowflakeRecipientRepository({"account": "acct"})

        with pytest.raises(RuntimeError, match="No recipients found"):
            repo.get_all()

        mock_conn.close.assert_called_once()


# ── FileTemplateLoader ───────────────────────────────────────────────


class TestFileTemplateLoader:
    def test_loads_html(self, tmp_path):
        html_file = tmp_path / "template.html"
        html_file.write_text("<html>Test</html>", encoding="utf-8")

        loader = FileTemplateLoader(html_file)
        result = loader.load()

        assert result == "<html>Test</html>"

    def test_missing_file_raises(self, tmp_path):
        missing = tmp_path / "missing.html"

        loader = FileTemplateLoader(missing)

        with pytest.raises(FileNotFoundError, match="HTML template not found"):
            loader.load()


# ── EcomailSender ────────────────────────────────────────────────────


class TestEcomailSender:
    @patch("maisignal.adapters.ecomail_sender.requests.post")
    def test_success_returns_true(self, mock_post, sample_payload):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.ok = True
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        sender = EcomailSender("test-key", "https://api.example.com")
        result = sender.send(sample_payload)

        assert result is True
        mock_post.assert_called_once()

    @patch("maisignal.adapters.ecomail_sender.requests.post")
    def test_api_error_returns_false(self, mock_post, sample_payload):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        sender = EcomailSender("test-key", "https://api.example.com")
        result = sender.send(sample_payload)

        assert result is False

    @patch("maisignal.adapters.ecomail_sender.requests.post")
    def test_network_error_raises(self, mock_post, sample_payload):
        mock_post.side_effect = requests.ConnectionError("Connection refused")

        sender = EcomailSender("test-key", "https://api.example.com")

        with pytest.raises(requests.ConnectionError):
            sender.send(sample_payload)

    @patch("maisignal.adapters.ecomail_sender.requests.post")
    def test_headers_and_timeout(self, mock_post, sample_payload):
        mock_post.return_value = MagicMock(spec=requests.Response, ok=True)

        sender = EcomailSender("my-key", "https://api.example.com")
        sender.send(sample_payload)

        call_kwargs = mock_post.call_args
        headers = call_kwargs.kwargs["headers"]
        assert headers["Content-Type"] == "application/json"
        assert headers["key"] == "my-key"
        assert call_kwargs.kwargs["timeout"] == 30
