"""appleJuice Server /info.json client."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp

from .const import TIMEOUT

_LOGGER = logging.getLogger(__name__)


class AppleJuiceError(Exception):
    """Base error of the appleJuice Server client."""


class AppleJuiceConnectionError(AppleJuiceError):
    """Server is not reachable or returned an invalid answer."""


class AppleJuiceAuthError(AppleJuiceError):
    """Server rejected the credentials."""


class AppleJuiceClient:
    """Small async client for the server's /info.json."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        username: str,
        password: str,
        tls: bool,
    ) -> None:
        """Initialize the client."""
        self._session = session
        self._base = f"{'https' if tls else 'http'}://{host}:{port}"
        self._auth = aiohttp.BasicAuth(username, password)

    async def get_info(self) -> dict[str, Any]:
        """Fetch /info.json and return the parsed document."""
        _LOGGER.debug("GET %s/info.json", self._base)
        try:
            async with asyncio.timeout(TIMEOUT):
                async with self._session.get(f"{self._base}/info.json", auth=self._auth) as response:
                    if response.status in (401, 403):
                        raise AppleJuiceAuthError("invalid credentials")
                    response.raise_for_status()
                    text = await response.text()
        except TimeoutError as err:
            raise AppleJuiceConnectionError("timeout") from err
        except aiohttp.ClientError as err:
            raise AppleJuiceConnectionError(str(err)) from err

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as err:
            raise AppleJuiceConnectionError("invalid JSON from /info.json") from err
        if not isinstance(parsed, dict):
            raise AppleJuiceConnectionError("unexpected /info.json format")
        return parsed
