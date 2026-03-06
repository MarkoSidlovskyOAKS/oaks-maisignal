"""Snowflake adapter for logging notification send results."""

import logging

from snowflake.connector import SnowflakeConnection

logger = logging.getLogger(__name__)

INSERT_QUERY = (
    "INSERT INTO maisignal.l0.notification_log "
    "(user_email, company_name, alert_type, subject, status, ecomail_response) "
    "VALUES (%s, %s, %s, %s, %s, %s)"
)


class SnowflakeNotificationLogger:
    """Inserts notification results into the Snowflake notification_log table."""

    def __init__(self, connection: SnowflakeConnection) -> None:
        self._conn = connection

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
                INSERT_QUERY,
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
            logger.exception(
                "Failed to log notification for %s", user_email
            )
