"""Data update coordinator for the appleJuice Server integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AppleJuiceAuthError, AppleJuiceClient, AppleJuiceError
from .const import CONF_OPTION_POLLING_RATE, CONF_PORT, CONF_URL, DEFAULT_POLLING_RATE, DOMAIN

_LOGGER = logging.getLogger(__name__)

type AppleJuiceConfigEntry = ConfigEntry[AppleJuiceCoordinator]

# Coordinator-Schlüssel -> Metrik in /info.json
METRICS: dict[str, str] = {
    "globaluser": "applejuice_global_users",
    "globalfilecount": "applejuice_global_files",
    "globalfilesize": "applejuice_global_file_size_bytes",
    "user": "applejuice_local_users",
    "filecount": "applejuice_local_files",
    "filesize": "applejuice_local_file_size_bytes",
    "firewalled": "applejuice_firewalled_users",
    "open_connections": "applejuice_open_connections",
    "memory_used": "applejuice_memory_used_bytes",
    "memory_free": "applejuice_memory_free_bytes",
    "memory_max": "applejuice_memory_max_bytes",
    "upspeed_last_10_sec": "applejuice_upload_bytes_per_sec",
    "downspeed_last_10_sec": "applejuice_download_bytes_per_sec",
    "sended_sources": "applejuice_sources_sent",
    "sended_local_sources": "applejuice_local_sources_sent",
    "sended_searchmessages": "applejuice_search_messages_sent",
    "sended_firewallmessages": "applejuice_firewall_messages_sent",
    "sended_messages": "applejuice_messages_sent",
    "messagesize": "applejuice_traffic_bytes",
    "responded_i_asks": "applejuice_info_asks_responded",
    "searches": "applejuice_searches_processed",
    "open_sockettasks": "applejuice_socket_tasks_open",
}


def _metric(parsed: dict[str, Any], name: str) -> Any:
    metric = parsed.get(name)
    return metric.get("value") if isinstance(metric, dict) else None


def _as_int(parsed: dict[str, Any], name: str) -> int | None:
    value = _metric(parsed, name)
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


class AppleJuiceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls /info.json."""

    config_entry: AppleJuiceConfigEntry

    def __init__(self, hass: HomeAssistant, entry: AppleJuiceConfigEntry, client: AppleJuiceClient) -> None:
        """Initialize the coordinator."""
        self.client = client
        self.version: str | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=f"appleJuice Server {entry.data[CONF_URL]}:{entry.data[CONF_PORT]}",
            config_entry=entry,
            update_interval=timedelta(seconds=entry.options.get(CONF_OPTION_POLLING_RATE, DEFAULT_POLLING_RATE)),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and map /info.json."""
        try:
            parsed = await self.client.get_info()
        except AppleJuiceAuthError as err:
            raise ConfigEntryAuthFailed(translation_domain=DOMAIN, translation_key="invalid_auth") from err
        except AppleJuiceError as err:
            raise UpdateFailed(translation_domain=DOMAIN, translation_key="cannot_connect") from err

        data: dict[str, Any] = {key: _as_int(parsed, name) for key, name in METRICS.items()}
        health = _as_int(parsed, "applejuice_server_health")
        data["serverstatus_ok"] = None if health is None else health == 1
        version = _metric(parsed, "applejuice_build_info")
        self.version = str(version) if version is not None else None
        return data
