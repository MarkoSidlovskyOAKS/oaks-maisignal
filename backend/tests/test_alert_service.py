"""Tests for the AlertService domain logic."""

from unittest.mock import MagicMock

import pytest

from maisignal.domain.alert_service import ALERT_TYPE, AlertService, build_payload
from maisignal.domain.models import Recipient, SendResult

# ── build_payload ────────────────────────────────────────────────────


class TestBuildPayload:
    def test_structure(self, sample_html, sample_recipient):
        payload = build_payload(sample_html, sample_recipient)

        msg = payload["message"]
        assert "subject" in msg
        assert "from_name" in msg
        assert "from_email" in msg
        assert "to" in msg
        assert "html" in msg
        assert "text" in msg
        assert "options" in msg

    def test_html_content_included(self, sample_html, sample_recipient):
        payload = build_payload(sample_html, sample_recipient)

        assert payload["message"]["html"] == sample_html

    def test_tracking_options_enabled(self, sample_html, sample_recipient):
        payload = build_payload(sample_html, sample_recipient)
        options = payload["message"]["options"]

        assert options["click_tracking"] is True
        assert options["open_tracking"] is True

    def test_recipient(self, sample_html, sample_recipient):
        payload = build_payload(sample_html, sample_recipient)
        recipients = payload["message"]["to"]

        assert len(recipients) == 1
        assert recipients[0]["email"] == sample_recipient.email
        assert recipients[0]["name"] == sample_recipient.name


# ── AlertService.send_alerts ─────────────────────────────────────────


class TestSendAlerts:
    def _make_service(
        self, repo=None, loader=None, sender=None, notification_logger=None
    ):
        return AlertService(
            recipient_repo=repo or MagicMock(),
            template_loader=loader or MagicMock(),
            email_sender=sender or MagicMock(),
            notification_logger=notification_logger,
        )

    def test_success_single_recipient(self, sample_html):
        repo = MagicMock()
        repo.get_all.return_value = [
            Recipient(email="a@example.com", name="Company A"),
        ]
        loader = MagicMock()
        loader.load.return_value = sample_html
        sender = MagicMock()
        sender.send.return_value = SendResult(success=True, response_text="ok")

        service = self._make_service(repo, loader, sender)
        service.send_alerts()

        loader.load.assert_called_once()
        repo.get_all.assert_called_once()
        sender.send.assert_called_once()

    def test_success_multiple_recipients(self, sample_html):
        repo = MagicMock()
        repo.get_all.return_value = [
            Recipient(email="a@example.com", name="Company A"),
            Recipient(email="b@example.com", name="Company B"),
        ]
        loader = MagicMock()
        loader.load.return_value = sample_html
        sender = MagicMock()
        sender.send.return_value = SendResult(success=True, response_text="ok")

        service = self._make_service(repo, loader, sender)
        service.send_alerts()

        assert sender.send.call_count == 2

    def test_partial_failure_raises(self, sample_html):
        repo = MagicMock()
        repo.get_all.return_value = [
            Recipient(email="a@example.com", name="Company A"),
            Recipient(email="b@example.com", name="Company B"),
        ]
        loader = MagicMock()
        loader.load.return_value = sample_html
        sender = MagicMock()
        sender.send.side_effect = [
            SendResult(success=True, response_text="ok"),
            SendResult(success=False, response_text="error"),
        ]

        service = self._make_service(repo, loader, sender)

        with pytest.raises(RuntimeError, match="1 of 2 sends failed"):
            service.send_alerts()

    def test_all_fail_raises(self, sample_html):
        repo = MagicMock()
        repo.get_all.return_value = [
            Recipient(email="a@example.com", name="Company A"),
        ]
        loader = MagicMock()
        loader.load.return_value = sample_html
        sender = MagicMock()
        sender.send.return_value = SendResult(
            success=False, response_text="error"
        )

        service = self._make_service(repo, loader, sender)

        with pytest.raises(RuntimeError, match="1 of 1 sends failed"):
            service.send_alerts()

    def test_network_error_raises(self, sample_html):
        repo = MagicMock()
        repo.get_all.return_value = [
            Recipient(email="a@example.com", name="Company A"),
        ]
        loader = MagicMock()
        loader.load.return_value = sample_html
        sender = MagicMock()
        sender.send.side_effect = ConnectionError("timeout")

        service = self._make_service(repo, loader, sender)

        with pytest.raises(RuntimeError, match="1 of 1 sends failed"):
            service.send_alerts()

    def test_calls_ports_in_order(self, sample_html):
        call_order = []

        repo = MagicMock()
        repo.get_all.side_effect = lambda: (
            call_order.append("repo"),
            [Recipient(email="a@example.com", name="A")],
        )[1]
        loader = MagicMock()
        loader.load.side_effect = lambda: (
            call_order.append("loader"),
            sample_html,
        )[1]
        sender = MagicMock()
        sender.send.side_effect = lambda p: (
            call_order.append("sender"),
            SendResult(success=True, response_text="ok"),
        )[1]

        service = self._make_service(repo, loader, sender)
        service.send_alerts()

        assert call_order == ["loader", "repo", "sender"]


# ── Notification logging ────────────────────────────────────────────


class TestNotificationLogging:
    def _make_service(self, sender, notification_logger):
        repo = MagicMock()
        repo.get_all.return_value = [
            Recipient(email="a@example.com", name="Company A"),
        ]
        loader = MagicMock()
        loader.load.return_value = "<html></html>"
        return AlertService(repo, loader, sender, notification_logger)

    def test_logs_successful_send(self):
        sender = MagicMock()
        sender.send.return_value = SendResult(
            success=True, response_text='{"status":"ok"}'
        )
        mock_logger = MagicMock()

        service = self._make_service(sender, mock_logger)
        service.send_alerts()

        mock_logger.log.assert_called_once()
        kwargs = mock_logger.log.call_args.kwargs
        assert kwargs["user_email"] == "a@example.com"
        assert kwargs["company_name"] == "Company A"
        assert kwargs["status"] == "sent"
        assert kwargs["alert_type"] == ALERT_TYPE
        assert kwargs["ecomail_response"] == '{"status":"ok"}'

    def test_logs_failed_send(self):
        sender = MagicMock()
        sender.send.return_value = SendResult(
            success=False, response_text="Unauthorized"
        )
        mock_logger = MagicMock()

        service = self._make_service(sender, mock_logger)

        with pytest.raises(RuntimeError):
            service.send_alerts()

        mock_logger.log.assert_called_once()
        kwargs = mock_logger.log.call_args.kwargs
        assert kwargs["status"] == "failed"
        assert kwargs["ecomail_response"] == "Unauthorized"

    def test_logs_network_error(self):
        sender = MagicMock()
        sender.send.side_effect = ConnectionError("Connection refused")
        mock_logger = MagicMock()

        service = self._make_service(sender, mock_logger)

        with pytest.raises(RuntimeError):
            service.send_alerts()

        mock_logger.log.assert_called_once()
        kwargs = mock_logger.log.call_args.kwargs
        assert kwargs["status"] == "failed"
        assert kwargs["ecomail_response"] == "Connection refused"

    def test_no_logger_does_not_fail(self):
        sender = MagicMock()
        sender.send.return_value = SendResult(
            success=True, response_text="ok"
        )

        service = self._make_service(sender, notification_logger=None)
        service.send_alerts()  # Should not raise

    def test_logs_for_each_recipient(self):
        repo = MagicMock()
        repo.get_all.return_value = [
            Recipient(email="a@example.com", name="Company A"),
            Recipient(email="b@example.com", name="Company B"),
        ]
        loader = MagicMock()
        loader.load.return_value = "<html></html>"
        sender = MagicMock()
        sender.send.return_value = SendResult(
            success=True, response_text="ok"
        )
        mock_logger = MagicMock()

        service = AlertService(repo, loader, sender, mock_logger)
        service.send_alerts()

        assert mock_logger.log.call_count == 2
        recipients_logged = [
            c.kwargs["user_email"] for c in mock_logger.log.call_args_list
        ]
        assert recipients_logged == ["a@example.com", "b@example.com"]
