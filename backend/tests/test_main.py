"""Tests for the MAiSIGNAL entry point (__main__.py)."""

from unittest.mock import MagicMock, patch

import pytest

from maisignal.__main__ import load_config, main

# ── load_config ──────────────────────────────────────────────────────


class TestLoadConfig:
    def test_success_with_env_file(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "ECOMAIL_API_KEY=secret-key-123\n"  # pragma: allowlist secret
            "SNOWFLAKE_ACCOUNT=acct\n"
            "SNOWFLAKE_USER=usr\n"
            "SNOWFLAKE_PASSWORD=pwd\n"
            "SNOWFLAKE_ROLE=role\n"
            "SNOWFLAKE_WAREHOUSE=wh\n"
        )
        monkeypatch.delenv("ECOMAIL_API_KEY", raising=False)
        monkeypatch.delenv("SNOWFLAKE_ACCOUNT", raising=False)
        monkeypatch.delenv("SNOWFLAKE_USER", raising=False)
        monkeypatch.delenv("SNOWFLAKE_PASSWORD", raising=False)
        monkeypatch.delenv("SNOWFLAKE_ROLE", raising=False)
        monkeypatch.delenv("SNOWFLAKE_WAREHOUSE", raising=False)

        api_key, sf_config = load_config(env_file)

        assert api_key == "secret-key-123"  # pragma: allowlist secret
        assert sf_config["account"] == "acct"
        assert sf_config["user"] == "usr"
        assert sf_config["password"] == "pwd"  # pragma: allowlist secret
        assert sf_config["role"] == "role"
        assert sf_config["warehouse"] == "wh"

    def test_success_without_env_file(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ECOMAIL_API_KEY", "env-key")
        monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "acct")
        monkeypatch.setenv("SNOWFLAKE_USER", "usr")
        monkeypatch.setenv("SNOWFLAKE_PASSWORD", "pwd")
        monkeypatch.setenv("SNOWFLAKE_ROLE", "role")
        monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "wh")
        missing = tmp_path / "nonexistent" / ".env"

        api_key, sf_config = load_config(missing)

        assert api_key == "env-key"  # pragma: allowlist secret
        assert sf_config["account"] == "acct"

    def test_missing_api_key_raises(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("OTHER_VAR=value\n")
        monkeypatch.delenv("ECOMAIL_API_KEY", raising=False)

        with pytest.raises(ValueError, match="ECOMAIL_API_KEY is not set"):
            load_config(env_file)

    def test_missing_snowflake_vars_raises(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("ECOMAIL_API_KEY=key\n")
        monkeypatch.delenv("SNOWFLAKE_ACCOUNT", raising=False)
        monkeypatch.delenv("SNOWFLAKE_USER", raising=False)
        monkeypatch.delenv("SNOWFLAKE_PASSWORD", raising=False)
        monkeypatch.delenv("SNOWFLAKE_ROLE", raising=False)
        monkeypatch.delenv("SNOWFLAKE_WAREHOUSE", raising=False)

        with pytest.raises(ValueError, match="Missing Snowflake env vars"):
            load_config(env_file)


# ── main ─────────────────────────────────────────────────────────────


class TestMain:
    @patch("maisignal.__main__.AlertService")
    @patch("maisignal.__main__.SnowflakeNotificationLogger")
    @patch("maisignal.__main__.EcomailSender")
    @patch("maisignal.__main__.FileTemplateLoader")
    @patch("maisignal.__main__.SnowflakeRecipientRepository")
    @patch("maisignal.__main__.snowflake.connector.connect")
    @patch("maisignal.__main__.load_config")
    def test_success(
        self, mock_config, mock_connect, mock_repo_cls, mock_loader_cls,
        mock_sender_cls, mock_notif_cls, mock_service_cls,
    ):
        mock_config.return_value = ("test-key", {"account": "acct"})
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service

        main()

        mock_config.assert_called_once()
        mock_connect.assert_called_once_with(account="acct")
        mock_repo_cls.assert_called_once_with(mock_conn)
        mock_loader_cls.assert_called_once()
        mock_sender_cls.assert_called_once()
        mock_notif_cls.assert_called_once_with(mock_conn)
        mock_service.send_alerts.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("maisignal.__main__.load_config")
    def test_config_error_exits(self, mock_config):
        mock_config.side_effect = ValueError("ECOMAIL_API_KEY is not set.")

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    @patch("maisignal.__main__.AlertService")
    @patch("maisignal.__main__.SnowflakeNotificationLogger")
    @patch("maisignal.__main__.EcomailSender")
    @patch("maisignal.__main__.FileTemplateLoader")
    @patch("maisignal.__main__.SnowflakeRecipientRepository")
    @patch("maisignal.__main__.snowflake.connector.connect")
    @patch("maisignal.__main__.load_config")
    def test_runtime_error_exits(
        self, mock_config, mock_connect, mock_repo_cls, mock_loader_cls,
        mock_sender_cls, mock_notif_cls, mock_service_cls,
    ):
        mock_config.return_value = ("test-key", {"account": "acct"})
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_service = MagicMock()
        mock_service.send_alerts.side_effect = RuntimeError("1 of 1 sends failed.")
        mock_service_cls.return_value = mock_service

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        mock_conn.close.assert_called_once()

    @patch("maisignal.__main__.AlertService")
    @patch("maisignal.__main__.SnowflakeNotificationLogger")
    @patch("maisignal.__main__.EcomailSender")
    @patch("maisignal.__main__.FileTemplateLoader")
    @patch("maisignal.__main__.SnowflakeRecipientRepository")
    @patch("maisignal.__main__.snowflake.connector.connect")
    @patch("maisignal.__main__.load_config")
    def test_file_not_found_exits(
        self, mock_config, mock_connect, mock_repo_cls, mock_loader_cls,
        mock_sender_cls, mock_notif_cls, mock_service_cls,
    ):
        mock_config.return_value = ("test-key", {"account": "acct"})
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_service = MagicMock()
        mock_service.send_alerts.side_effect = FileNotFoundError("Template missing")
        mock_service_cls.return_value = mock_service

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        mock_conn.close.assert_called_once()
