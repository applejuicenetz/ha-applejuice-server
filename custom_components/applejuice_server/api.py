"""appleJuice Server."""

import asyncio
import logging
import aiohttp
from homeassistant.core import HomeAssistant
from typing import Optional
from homeassistant.helpers import aiohttp_client

_LOGGER = logging.getLogger(__name__)


async def get_raw_data(hass: HomeAssistant, url: str, port: int, username: str, password: str, tls: bool, endpoint: str):
    """Fetch RAW data asynchronously using aiohttp."""

    session = aiohttp_client.async_get_clientsession(hass)

    try:
        protocol = "https" if tls else "http"
        full_url = f"{protocol}://{url}:{port}{endpoint}"

        _LOGGER.debug("call url: %s", full_url)

        async with asyncio.timeout(10):
            async with session.get(full_url, auth=aiohttp.BasicAuth(username, password)) as response:
                response.raise_for_status()
                return await response.text()

    except aiohttp.ClientError as e:
        _LOGGER.error("Error while fetching RAW data: %s", e)

    return None
