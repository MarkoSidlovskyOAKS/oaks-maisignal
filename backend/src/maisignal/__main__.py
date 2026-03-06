"""MAiSIGNAL entry point – wire adapters and run the alert service."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from maisignal.adapters.ecomail_sender import EcomailSender
from maisignal.adapters.file_template_loader import FileTemplateLoader
from maisignal.adapters.snowflake_repository import SnowflakeRecipientRepository
from maisignal.domain.alert_service import AlertService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BACKEND_DIR / "config" / ".env"
HTML_FILE = BACKEND_DIR / "templates" / "sukl-alert-email-real-data.html"
ECOMAIL_URL = "https://api2.ecomailapp.cz/transactional/send-message"

SNOWFLAKE_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
]


def load_config(env_path: Path = ENV_PATH) -> tuple[str, dict]:
    """Load .env and return (ecomail_api_key, snowflake_config).

    Raises:
        ValueError: If required environment variables are missing.
    """
    if env_path.is_file():
        load_dotenv(env_path)
        logger.info("Loaded .env from %s", env_path)

    api_key = os.getenv("ECOMAIL_API_KEY")
    if not api_key:
        raise ValueError("ECOMAIL_API_KEY is not set.")

    missing = [v for v in SNOWFLAKE_ENV_VARS if not os.getenv(v)]
    if missing:
        raise ValueError(
            f"Missing Snowflake env vars: {', '.join(missing)}"
        )

    sf_config = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    }

    return api_key, sf_config


def main() -> None:
    """Wire adapters, create AlertService, and send alerts."""
    try:
        api_key, sf_config = load_config()
    except ValueError as exc:
        logger.error(str(exc))
        sys.exit(1)

    repo = SnowflakeRecipientRepository(sf_config)
    loader = FileTemplateLoader(HTML_FILE)
    sender = EcomailSender(api_key, ECOMAIL_URL)

    service = AlertService(repo, loader, sender)

    try:
        service.send_alerts()
    except (RuntimeError, FileNotFoundError) as exc:
        logger.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
