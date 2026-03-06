"""Port definitions (interfaces) for MAiSIGNAL."""

from typing import Protocol

from maisignal.domain.models import Recipient


class RecipientRepository(Protocol):
    """Fetches alert recipients."""

    def get_all(self) -> list[Recipient]: ...


class TemplateLoader(Protocol):
    """Loads the HTML email template."""

    def load(self) -> str: ...


class EmailSender(Protocol):
    """Sends a transactional email."""

    def send(self, payload: dict) -> bool: ...
