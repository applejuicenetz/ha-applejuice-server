"""appleJuice Server integration for Home Assistant."""

import asyncio
import logging
import json
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import (
    DOMAIN,
    CONF_URL,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_TLS,
    PLATFORMS,
    CONF_OPTION_POLLING_RATE,
    TIMEOUT,
)

from .api import get_raw_data

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)

_LOGGER.debug("loading appleJuice Server init")


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the appleJuice Server integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    hass.data[DOMAIN][entry.entry_id].config_entry = entry
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if await hass.config_entries.async_forward_entry_unload(entry, "sensor"):
        hass.data[DOMAIN].pop(entry.entry_id)
        return True
    return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""

    global SCAN_INTERVAL

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    if entry.options.get(CONF_OPTION_POLLING_RATE) is not None:
        SCAN_INTERVAL = timedelta(seconds=entry.options.get(CONF_OPTION_POLLING_RATE))
    else:
        SCAN_INTERVAL = timedelta(seconds=30)

    coordinator = AppleJuiceCoordinator(hass, config_entry=entry)

    await coordinator.async_config_entry_first_refresh()

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        coordinator.platforms.append(platform)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


class AppleJuiceCoordinator(DataUpdateCoordinator):
    """Handles periodic JSON data retrieval."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize the coordinator with update interval settings."""
        self.system = None
        self.version = None
        self.platforms = []
        self.updaters = [
            _async_update_info_json,
        ]
        self.hass = hass
        self.config_entry = config_entry

        self.name = f"appleJuice Server {config_entry.data.get(CONF_URL)}:{config_entry.data.get(CONF_PORT)}"

        super().__init__(hass, _LOGGER, name=self.name, update_interval=SCAN_INTERVAL, always_update=False)

    async def _async_update_data(self):
        """Update data via library."""
        combined_data = {}

        for updater in self.updaters:
            data = await updater(self)
            if data is not None:
                combined_data.update(data)

        _LOGGER.debug("combined_data: %s", combined_data)

        return combined_data


async def _async_update_info_json(self):
    """Fetch JSON data asynchronously."""
    info_data = await get_raw_data(
        self.hass,
        self.config_entry.data.get(CONF_URL),
        self.config_entry.data.get(CONF_PORT),
        self.config_entry.data.get(CONF_USERNAME),
        self.config_entry.data.get(CONF_PASSWORD),
        self.config_entry.data.get(CONF_TLS),
        "/info.json",
    )

    if not info_data:
        return {}

    try:
        parsed_data = json.loads(info_data)
    except json.JSONDecodeError as exc:
        _LOGGER.error("Failed to decode /info.json: %s", exc)
        return {}

    def _value(metric_key: str):
        metric = parsed_data.get(metric_key)
        if isinstance(metric, dict):
            return metric.get("value")
        return None

    def _as_int(metric_key: str):
        value = _value(metric_key)
        return int(value) if value is not None else None

    server_health = _as_int("applejuice_server_health")

    return {
        "globaluser": _as_int("applejuice_global_users"),
        "globalfilecount": _as_int("applejuice_global_files"),
        "globalfilesize": _as_int("applejuice_global_file_size_bytes"),
        "user": _as_int("applejuice_local_users"),
        "filecount": _as_int("applejuice_local_files"),
        "filesize": _as_int("applejuice_local_file_size_bytes"),
        "firewalled": _as_int("applejuice_firewalled_users"),
        "open_connections": _as_int("applejuice_open_connections"),
        "memory_used": _as_int("applejuice_memory_used_bytes"),
        "memory_free": _as_int("applejuice_memory_free_bytes"),
        "memory_max": _as_int("applejuice_memory_max_bytes"),
        "upspeed_last_10_sec": _as_int("applejuice_upload_bytes_per_sec"),
        "downspeed_last_10_sec": _as_int("applejuice_download_bytes_per_sec"),
        "serverstatus_ok": server_health == 1 if server_health is not None else None,
        "sended_sources": _as_int("applejuice_sources_sent"),
        "sended_local_sources": _as_int("applejuice_local_sources_sent"),
        "sended_searchmessages": _as_int("applejuice_search_messages_sent"),
        "sended_firewallmessages": _as_int("applejuice_firewall_messages_sent"),
        "sended_messages": _as_int("applejuice_messages_sent"),
        "messagesize": _as_int("applejuice_traffic_bytes"),
        "responded_i_asks": _as_int("applejuice_info_asks_responded"),
        "searches": _as_int("applejuice_searches_processed"),
        "open_sockettasks": _as_int("applejuice_socket_tasks_open"),
    }
