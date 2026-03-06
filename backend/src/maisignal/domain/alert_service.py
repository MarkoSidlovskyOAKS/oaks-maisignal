"""Core use case: send MAiSIGNAL email alerts."""

from __future__ import annotations

import logging

from maisignal.domain.models import Recipient
from maisignal.ports import (
    EmailSender,
    NotificationLogger,
    RecipientRepository,
    TemplateLoader,
)

logger = logging.getLogger(__name__)

ALERT_TYPE = "sukl_unavailability"


def build_payload(html_content: str, recipient: Recipient) -> dict:
    """Build the Ecomail transactional email payload."""
    return {
        "message": {
            "subject": (
                "\u26a0\ufe0f MAiSIGNAL: V\u00fdpadek LP"
                " \u2013 LYRICA (Pregabalin)"
            ),
            "from_name": "MAiSIGNAL Alerts",
            "from_email": "alerts@mailing.oaks.cz",
            "reply_to": "noreply@mailing.oaks.cz",
            "to": [
                {
                    "email": recipient.email,
                    "name": recipient.name,
                }
            ],
            "html": html_content,
            "text": (
                "MAiSIGNAL Alert - Vypadek LP: LYRICA (Pregabalin). "
                "Duvod: Preruseni dodavky. Platnost od: 2025-01-01. "
                "Zdroj: SUKL - Hlaseni nedostupnosti. "
                "Vice informaci v HTML verzi emailu."
            ),
            "options": {
                "click_tracking": True,
                "open_tracking": True,
            },
        }
    }


class AlertService:
    """Orchestrates fetching recipients, loading templates, and sending alerts."""

    def __init__(
        self,
        recipient_repo: RecipientRepository,
        template_loader: TemplateLoader,
        email_sender: EmailSender,
        notification_logger: NotificationLogger | None = None,
    ) -> None:
        self._recipient_repo = recipient_repo
        self._template_loader = template_loader
        self._email_sender = email_sender
        self._notification_logger = notification_logger

    def send_alerts(self) -> None:
        """Load template, fetch recipients, build payloads, and send emails.

        Raises:
            RuntimeError: If any sends fail.
        """
        html_content = self._template_loader.load()
        recipients = self._recipient_repo.get_all()

        logger.info("Sending alerts to %d recipients...", len(recipients))
        failures = 0

        for recipient in recipients:
            payload = build_payload(html_content, recipient)
            subject = payload["message"]["subject"]

            try:
                result = self._email_sender.send(payload)
            except Exception as exc:
                logger.error("Network error sending alert: %s", exc)
                self._log_notification(
                    recipient, subject, "failed", str(exc)
                )
                failures += 1
                continue

            if result.success:
                logger.info("Alert sent successfully.")
                self._log_notification(
                    recipient, subject, "sent", result.response_text
                )
            else:
                logger.error("Failed to send alert.")
                self._log_notification(
                    recipient, subject, "failed", result.response_text
                )
                failures += 1

        if failures:
            raise RuntimeError(
                f"{failures} of {len(recipients)} sends failed."
            )

        logger.info("All %d alerts sent successfully.", len(recipients))

    def _log_notification(
        self,
        recipient: Recipient,
        subject: str,
        status: str,
        ecomail_response: str,
    ) -> None:
        """Delegate to notification logger if one is configured."""
        if self._notification_logger is not None:
            self._notification_logger.log(
                user_email=recipient.email,
                company_name=recipient.name,
                alert_type=ALERT_TYPE,
                subject=subject,
                status=status,
                ecomail_response=ecomail_response,
            )
