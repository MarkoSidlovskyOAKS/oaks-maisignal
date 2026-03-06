"""Tests for send_maisignal_alert module."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from send_maisignal_alert import (
    build_payload,
    load_config,
    load_template,
    main,
    send_alert,
)

# ── load_config ──────────────────────────────────────────────────────


class TestLoadConfig:
    def test_success_with_env_file(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("ECOMAIL_API_KEY=secret-key-123\n")
        monkeypatch.delenv("ECOMAIL_API_KEY", raising=False)

        result = load_config(env_file)

        assert result == "secret-key-123"

    def test_success_without_env_file(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ECOMAIL_API_KEY", "env-var-key")
        missing = tmp_path / "nonexistent" / ".env"

        result = load_config(missing)

        assert result == "env-var-key"

    def test_missing_api_key_raises(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("OTHER_VAR=value\n")
        monkeypatch.delenv("ECOMAIL_API_KEY", raising=False)

        with pytest.raises(ValueError, match="ECOMAIL_API_KEY is not set"):
            load_config(env_file)


# ── load_template ────────────────────────────────────────────────────


class TestLoadTemplate:
    def test_success(self, tmp_path):
        html_file = tmp_path / "template.html"
        html_file.write_text("<html>Test</html>", encoding="utf-8")

        result = load_template(html_file)

        assert result == "<html>Test</html>"

    def test_missing_file_raises(self, tmp_path):
        missing = tmp_path / "missing.html"

        with pytest.raises(FileNotFoundError, match="HTML template not found"):
            load_template(missing)


# ── build_payload ────────────────────────────────────────────────────


class TestBuildPayload:
    def test_structure(self, sample_html):
        payload = build_payload(sample_html)

        assert "message" in payload
        msg = payload["message"]
        assert "subject" in msg
        assert "from_name" in msg
        assert "from_email" in msg
        assert "to" in msg
        assert "html" in msg
        assert "text" in msg
        assert "options" in msg

    def test_html_content_included(self, sample_html):
        payload = build_payload(sample_html)

        assert payload["message"]["html"] == sample_html

    def test_tracking_options_enabled(self, sample_html):
        payload = build_payload(sample_html)
        options = payload["message"]["options"]

        assert options["click_tracking"] is True
        assert options["open_tracking"] is True

    def test_recipient(self, sample_html):
        payload = build_payload(sample_html)
        recipients = payload["message"]["to"]

        assert len(recipients) == 1
        assert "email" in recipients[0]
        assert "name" in recipients[0]


# ── send_alert ───────────────────────────────────────────────────────


class TestSendAlert:
    @patch("send_maisignal_alert.requests.post")
    def test_success(self, mock_post, sample_payload, sample_api_key):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.ok = True
        mock_post.return_value = mock_response

        response = send_alert(sample_payload, sample_api_key)

        assert response.status_code == 200
        mock_post.assert_called_once()

    @patch("send_maisignal_alert.requests.post")
    def test_api_error(self, mock_post, sample_payload, sample_api_key):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 401
        mock_response.ok = False
        mock_post.return_value = mock_response

        response = send_alert(sample_payload, sample_api_key)

        assert response.status_code == 401
        assert not response.ok

    @patch("send_maisignal_alert.requests.post")
    def test_network_error(self, mock_post, sample_payload, sample_api_key):
        mock_post.side_effect = requests.ConnectionError("Connection refused")

        with pytest.raises(requests.ConnectionError):
            send_alert(sample_payload, sample_api_key)

    @patch("send_maisignal_alert.requests.post")
    def test_headers(self, mock_post, sample_payload, sample_api_key):
        mock_post.return_value = MagicMock(spec=requests.Response)

        send_alert(sample_payload, sample_api_key)

        call_kwargs = mock_post.call_args
        headers = call_kwargs.kwargs["headers"]
        assert headers["Content-Type"] == "application/json"
        assert headers["key"] == sample_api_key

    @patch("send_maisignal_alert.requests.post")
    def test_timeout(self, mock_post, sample_payload, sample_api_key):
        mock_post.return_value = MagicMock(spec=requests.Response)

        send_alert(sample_payload, sample_api_key)

        call_kwargs = mock_post.call_args
        assert call_kwargs.kwargs["timeout"] == 30


# ── main ─────────────────────────────────────────────────────────────


class TestMain:
    @patch("send_maisignal_alert.send_alert")
    @patch("send_maisignal_alert.load_template")
    @patch("send_maisignal_alert.load_config")
    def test_success(self, mock_config, mock_template, mock_send):
        mock_config.return_value = "test-key"
        mock_template.return_value = "<html>ok</html>"
        mock_response = MagicMock(spec=requests.Response)
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = '{"status": "ok"}'
        mock_send.return_value = mock_response

        main()

        mock_config.assert_called_once()
        mock_template.assert_called_once()
        mock_send.assert_called_once()

    @patch("send_maisignal_alert.load_config")
    def test_config_error_exits(self, mock_config):
        mock_config.side_effect = ValueError("ECOMAIL_API_KEY is not set.")

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    @patch("send_maisignal_alert.load_template")
    @patch("send_maisignal_alert.load_config")
    def test_template_error_exits(self, mock_config, mock_template):
        mock_config.return_value = "test-key"
        mock_template.side_effect = FileNotFoundError("HTML template not found")

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    @patch("send_maisignal_alert.send_alert")
    @patch("send_maisignal_alert.load_template")
    @patch("send_maisignal_alert.load_config")
    def test_api_error_exits(self, mock_config, mock_template, mock_send):
        mock_config.return_value = "test-key"
        mock_template.return_value = "<html>ok</html>"
        mock_response = MagicMock(spec=requests.Response)
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_send.return_value = mock_response

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    @patch("send_maisignal_alert.send_alert")
    @patch("send_maisignal_alert.load_template")
    @patch("send_maisignal_alert.load_config")
    def test_network_error_exits(self, mock_config, mock_template, mock_send):
        mock_config.return_value = "test-key"
        mock_template.return_value = "<html>ok</html>"
        mock_send.side_effect = requests.ConnectionError("timeout")

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
