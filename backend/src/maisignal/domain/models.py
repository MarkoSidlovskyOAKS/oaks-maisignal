"""Domain models for MAiSIGNAL."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Recipient:
    """An email alert recipient."""

    email: str
    name: str
