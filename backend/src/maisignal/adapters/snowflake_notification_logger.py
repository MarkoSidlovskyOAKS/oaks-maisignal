"""Snowflake adapter for logging notification send results."""

import logging

from snowflake.connector import SnowflakeConnection

logger = logging.getLogger(__name__)

ALLOWED_SCHEMAS = ("l0", "l0_dev", "l0_prod")


class SnowflakeNotificationLogger:
    """Inserts notification results into the Snowflake notification_log table."""

    def __init__(
        self, connection: SnowflakeConnection, schema: str = "l0"
    ) -> None:
        if schema not in ALLOWED_SCHEMAS:
            raise ValueError(
                f"Invalid schema '{schema}'. "
                f"Allowed: {', '.join(ALLOWED_SCHEMAS)}"
            )
        self._conn = connection
        self._query = (
            f"INSERT INTO maisignal.{schema}.notification_log "
            "(user_email, company_name, alert_type, subject, "
            "status, ecomail_response) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )

    def log(
        self,
        user_email: str,
        company_name: str,
        alert_type: str,
        subject: str,
        status: str,
        ecomail_response: str,
    ) -> None:
        """Insert a notification log row. Never raises — errors are logged."""
        try:
            cur = self._conn.cursor()
            cur.execute(
                self._query,
                (
                    user_email,
                    company_name,
                    alert_type,
                    subject,
                    status,
                    ecomail_response,
                ),
            )
        except Exception:
            logger.exception("Failed to log notification.")
