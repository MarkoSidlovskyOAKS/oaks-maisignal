"""MAiSIGNAL – Send transactional email alert via Ecomail API."""

import json
import logging
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BACKEND_DIR / "config" / ".env"
HTML_FILE = BACKEND_DIR / "templates" / "sukl-alert-email-real-data.html"
ECOMAIL_URL = "https://api2.ecomailapp.cz/transactional/send-message"


def load_config(env_path: Path = ENV_PATH) -> str:
    """Load .env (if exists) and return the ECOMAIL_API_KEY.

    The .env file is optional — the API key can also be set as an
    environment variable directly (e.g. via ``docker run -e``).

    Raises:
        ValueError: If ECOMAIL_API_KEY is not set.
    """
    if env_path.is_file():
        load_dotenv(env_path)
        logger.info("Loaded .env from %s", env_path)

    api_key = os.getenv("ECOMAIL_API_KEY")
    if not api_key:
        raise ValueError("ECOMAIL_API_KEY is not set.")
    return api_key


def load_template(template_path: Path = HTML_FILE) -> str:
    """Read and return the HTML email template.

    Raises:
        FileNotFoundError: If the template file does not exist.
    """
    if not template_path.is_file():
        raise FileNotFoundError(f"HTML template not found: {template_path}")
    html = template_path.read_text(encoding="utf-8")
    logger.info("Loaded HTML template (%d chars).", len(html))
    return html


def build_payload(html_content: str) -> dict:
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
                    "email": "marko.sidlovsky@oaks.cz",
                    "name": "Marko Sidlovsky",
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


def send_alert(
    payload: dict,
    api_key: str,
    url: str = ECOMAIL_URL,
) -> requests.Response:
    """POST the payload to the Ecomail transactional API.

    Returns:
        The :class:`requests.Response` object.
    """
    response = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "key": api_key,
        },
        data=json.dumps(payload),
        timeout=30,
    )
    return response


def main() -> None:
    """Orchestrate config loading, template reading, and alert sending."""
    try:
        api_key = load_config()
    except ValueError as exc:
        logger.error(str(exc))
        sys.exit(1)

    try:
        html_content = load_template()
    except FileNotFoundError as exc:
        logger.error(str(exc))
        sys.exit(1)

    payload = build_payload(html_content)
    logger.info("Sending alert via Ecomail API...")

    try:
        response = send_alert(payload, api_key)
    except requests.RequestException as exc:
        logger.error("Network error: %s", exc)
        sys.exit(1)

    logger.info("Response status: %d", response.status_code)
    logger.info("Response body: %s", response.text)

    if not response.ok:
        logger.error("Ecomail API returned an error.")
        sys.exit(1)

    logger.info("Alert sent successfully.")


if __name__ == "__main__":
    main()
