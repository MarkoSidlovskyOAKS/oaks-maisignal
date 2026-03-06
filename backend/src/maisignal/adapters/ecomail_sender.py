"""Ecomail API adapter for sending transactional emails."""

import json
import logging

import requests

from maisignal.domain.models import SendResult

logger = logging.getLogger(__name__)


class EcomailSender:
    """Sends transactional emails via the Ecomail REST API."""

    def __init__(self, api_key: str, url: str) -> None:
        self._api_key = api_key
        self._url = url

    def send(self, payload: dict) -> SendResult:
        """POST the payload to the Ecomail transactional API.

        Returns:
            SendResult with success flag and raw response text.

        Raises:
            requests.RequestException: On network-level errors.
        """
        response = requests.post(
            self._url,
            headers={
                "Content-Type": "application/json",
                "key": self._api_key,
            },
            data=json.dumps(payload),
            timeout=30,
        )

        if not response.ok:
            logger.error(
                "Ecomail API error (%d): %s",
                response.status_code,
                response.text,
            )
            return SendResult(success=False, response_text=response.text)

        return SendResult(success=True, response_text=response.text)
