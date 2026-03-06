"""Snowflake adapter for fetching email recipients."""

import logging

import snowflake.connector

from maisignal.domain.models import Recipient

logger = logging.getLogger(__name__)

RECIPIENTS_QUERY = (
    "SELECT user_email, company_name "
    "FROM maisignal.l0.client_portfolio"
)


class SnowflakeRecipientRepository:
    """Fetches recipients from the Snowflake client_portfolio table."""

    def __init__(self, sf_config: dict) -> None:
        self._sf_config = sf_config

    def get_all(self) -> list[Recipient]:
        """Connect to Snowflake, query recipients, and return them.

        Raises:
            RuntimeError: If no recipients are found.
        """
        conn = snowflake.connector.connect(**self._sf_config)
        try:
            cur = conn.cursor()
            cur.execute(RECIPIENTS_QUERY)
            rows = cur.fetchall()
        finally:
            conn.close()

        if not rows:
            raise RuntimeError("No recipients found in client_portfolio.")

        recipients = [Recipient(email=row[0], name=row[1]) for row in rows]
        logger.info("Fetched %d recipients from Snowflake.", len(recipients))
        return recipients
