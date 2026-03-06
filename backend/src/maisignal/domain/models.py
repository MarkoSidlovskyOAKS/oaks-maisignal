"""Domain models for MAiSIGNAL."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Recipient:
    """An email alert recipient."""

    email: str
    name: str


@dataclass(frozen=True)
class SendResult:
    """Outcome of a single email send attempt."""

    success: bool
    response_text: str
