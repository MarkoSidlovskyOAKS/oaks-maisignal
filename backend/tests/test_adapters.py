"""Tests for MAiSIGNAL infrastructure adapters."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from maisignal.adapters.ecomail_sender import EcomailSender
from maisignal.adapters.file_template_loader import FileTemplateLoader
from maisignal.adapters.snowflake_notification_logger import (
    SnowflakeNotificationLogger,
)
from maisignal.adapters.snowflake_repository import SnowflakeRecipientRepository
from maisignal.domain.models import Recipient, SendResult

# ── SnowflakeRecipientRepository ─────────────────────────────────────


class TestSnowflakeRecipientRepository:
    def test_returns_recipients(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("a@example.com", "Company A"),
            ("b@example.com", "Company B"),
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        repo = SnowflakeRecipientRepository(mock_conn)
        result = repo.get_all()

        assert result == [
            Recipient(email="a@example.com", name="Company A"),
            Recipient(email="b@example.com", name="Company B"),
        ]

    def test_empty_result_raises(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        repo = SnowflakeRecipientRepository(mock_conn)

        with pytest.raises(RuntimeError, match="No recipients found"):
            repo.get_all()


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
    def test_success_returns_send_result(self, mock_post, sample_payload):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = '{"status": "ok"}'
        mock_post.return_value = mock_response

        sender = EcomailSender("test-key", "https://api.example.com")
        result = sender.send(sample_payload)

        assert result == SendResult(success=True, response_text='{"status": "ok"}')
        mock_post.assert_called_once()

    @patch("maisignal.adapters.ecomail_sender.requests.post")
    def test_api_error_returns_failed_send_result(self, mock_post, sample_payload):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        sender = EcomailSender("test-key", "https://api.example.com")
        result = sender.send(sample_payload)

        assert result == SendResult(success=False, response_text="Unauthorized")

    @patch("maisignal.adapters.ecomail_sender.requests.post")
    def test_network_error_raises(self, mock_post, sample_payload):
        mock_post.side_effect = requests.ConnectionError("Connection refused")

        sender = EcomailSender("test-key", "https://api.example.com")

        with pytest.raises(requests.ConnectionError):
            sender.send(sample_payload)

    @patch("maisignal.adapters.ecomail_sender.requests.post")
    def test_headers_and_timeout(self, mock_post, sample_payload):
        mock_response = MagicMock(spec=requests.Response, ok=True)
        mock_response.text = ""
        mock_post.return_value = mock_response

        sender = EcomailSender("my-key", "https://api.example.com")
        sender.send(sample_payload)

        call_kwargs = mock_post.call_args
        headers = call_kwargs.kwargs["headers"]
        assert headers["Content-Type"] == "application/json"
        assert headers["key"] == "my-key"
        assert call_kwargs.kwargs["timeout"] == 30


# ── SnowflakeNotificationLogger ─────────────────────────────────────


class TestSnowflakeNotificationLogger:
    def test_inserts_log_row(self):
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        notif_logger = SnowflakeNotificationLogger(mock_conn)
        notif_logger.log(
            user_email="a@example.com",
            company_name="Company A",
            alert_type="sukl_unavailability",
            subject="Test Subject",
            status="sent",
            ecomail_response='{"status": "ok"}',
        )

        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args
        assert args[0][1] == (
            "a@example.com",
            "Company A",
            "sukl_unavailability",
            "Test Subject",
            "sent",
            '{"status": "ok"}',
        )

    def test_swallows_errors(self):
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("Cursor failed")

        notif_logger = SnowflakeNotificationLogger(mock_conn)
        # Should not raise
        notif_logger.log(
            user_email="a@example.com",
            company_name="Company A",
            alert_type="sukl_unavailability",
            subject="Test",
            status="sent",
            ecomail_response="",
        )
