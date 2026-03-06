"""Snowflake adapter for fetching email recipients."""

import logging

from snowflake.connector import SnowflakeConnection

from maisignal.domain.models import Recipient

logger = logging.getLogger(__name__)

RECIPIENTS_QUERY = (
    "SELECT user_email, company_name "
    "FROM maisignal.l0.client_portfolio"
)


class SnowflakeRecipientRepository:
    """Fetches recipients from the Snowflake client_portfolio table."""

    def __init__(self, connection: SnowflakeConnection) -> None:
        self._conn = connection

    def get_all(self) -> list[Recipient]:
        """Query recipients and return them.

        Raises:
            RuntimeError: If no recipients are found.
        """
        cur = self._conn.cursor()
        cur.execute(RECIPIENTS_QUERY)
        rows = cur.fetchall()

        if not rows:
            raise RuntimeError("No recipients found in client_portfolio.")

        recipients = [Recipient(email=row[0], name=row[1]) for row in rows]
        logger.info("Fetched %d recipients from Snowflake.", len(recipients))
        return recipients
