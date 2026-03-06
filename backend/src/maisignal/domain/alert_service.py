"""Core use case: send MAiSIGNAL email alerts."""

import logging

from maisignal.domain.models import Recipient
from maisignal.ports import EmailSender, RecipientRepository, TemplateLoader

logger = logging.getLogger(__name__)


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
    ) -> None:
        self._recipient_repo = recipient_repo
        self._template_loader = template_loader
        self._email_sender = email_sender

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
            try:
                success = self._email_sender.send(payload)
            except Exception as exc:
                logger.error(
                    "Network error sending to %s: %s", recipient.email, exc
                )
                failures += 1
                continue

            if success:
                logger.info("Alert sent to %s.", recipient.email)
            else:
                logger.error("Failed to send alert to %s.", recipient.email)
                failures += 1

        if failures:
            raise RuntimeError(
                f"{failures} of {len(recipients)} sends failed."
            )

        logger.info("All %d alerts sent successfully.", len(recipients))
