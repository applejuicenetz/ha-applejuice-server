"""appleJuice Server integration for Home Assistant."""

import asyncio
import logging
import re
import xmltodict
from datetime import timedelta

from re import sub

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
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
    """Handles periodic XML data retrieval."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize the coordinator with update interval settings."""
        self.system = None
        self.version = None
        self.platforms = []
        self.updaters = [
            _async_update_info,
            _async_update_status,
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


async def _async_update_info(self):
    """Fetch XML data asynchronously."""
    infoData = await get_raw_data(self.hass,
                                  self.config_entry.data.get(CONF_URL),
                                  self.config_entry.data.get(CONF_PORT),
                                  self.config_entry.data.get(CONF_USERNAME),
                                  self.config_entry.data.get(CONF_PASSWORD),
                                  self.config_entry.data.get(CONF_TLS),
                                  "/info.xml")

    parsed_data = xmltodict.parse(infoData)

    applejuiceserver = parsed_data.get("applejuiceserver")

    return {
        "globaluser": int(applejuiceserver.get("globaluser")) if applejuiceserver is not None else None,
        "globalfilecount": int(applejuiceserver.get("globalfilecount")) if applejuiceserver is not None else None,
        "globalfilesize": int(float(applejuiceserver.get("globalfilesize"))) if applejuiceserver is not None else None,
        "user": int(applejuiceserver.get("user")) if applejuiceserver is not None else None,
        "filecount": int(applejuiceserver.get("filecount")) if applejuiceserver is not None else None,
        "filesize": int(float(applejuiceserver.get("filesize"))) if applejuiceserver is not None else None,
    }


async def _async_update_status(self):
    """Fetch XML share data asynchronously."""
    statusData = await get_raw_data(self.hass,
                                    self.config_entry.data.get(CONF_URL),
                                    self.config_entry.data.get(CONF_PORT),
                                    self.config_entry.data.get(CONF_USERNAME),
                                    self.config_entry.data.get(CONF_PASSWORD),
                                    self.config_entry.data.get(CONF_TLS),
                                    "/status_raw.htm")

    parsedData = {}

    firewalled = re.compile(r'users \((\d+) firewalled\) share').search(statusData)
    parsedData['firewalled'] = int(firewalled.group(1)) if firewalled else None

    open_connections = re.compile(r'open connections: (\d+)').search(statusData)
    parsedData['open_connections'] = int(open_connections.group(1)) if open_connections else None

    memory_used = re.compile(r'used: (\d+) ').search(statusData)
    parsedData['memory_used'] = int(memory_used.group(1)) if memory_used else None

    memory_free = re.compile(r'free: (\d+) ').search(statusData)
    parsedData['memory_free'] = int(memory_free.group(1)) if memory_free else None

    memory_max = re.compile(r'max : (\d+) ').search(statusData)
    parsedData['memory_max'] = int(memory_max.group(1)) if memory_max else None

    upspeed_last_10_sec = re.compile(r'upspeed last 10 sec: (\d+\.\d+) ').search(statusData)
    parsedData['upspeed_last_10_sec'] = float(upspeed_last_10_sec.group(1)) if upspeed_last_10_sec else None

    downspeed_last_10_sec = re.compile(r'downspeed last 10 sec: (\d+\.\d+) ').search(statusData)
    parsedData['downspeed_last_10_sec'] = float(downspeed_last_10_sec.group(1)) if downspeed_last_10_sec else None

    parsedData['serverstatus_ok'] = ">ok<" in statusData

    sended_sources = re.compile(r'sended sources: (\d+)').search(statusData)
    parsedData['sended_sources'] = int(sended_sources.group(1)) if sended_sources else None

    sended_local_sources = re.compile(r'sended local sources: (\d+)').search(statusData)
    parsedData['sended_local_sources'] = int(sended_local_sources.group(1)) if sended_local_sources else None

    sended_searchmessages = re.compile(r'sended searchmessages: (\d+)').search(statusData)
    parsedData['sended_searchmessages'] = int(sended_searchmessages.group(1)) if sended_searchmessages else None

    sended_firewallmessages = re.compile(r'sended firewallmessages: (\d+)').search(statusData)
    parsedData['sended_firewallmessages'] = int(sended_firewallmessages.group(1)) if sended_firewallmessages else None

    sended_messages = re.compile(r'sended messages: (\d+)').search(statusData)
    parsedData['sended_messages'] = int(sended_messages.group(1)) if sended_messages else None

    messagesize = re.compile(r'messagesize: (\d+)').search(statusData)
    parsedData['messagesize'] = int(messagesize.group(1)) if messagesize else None

    responded_i_asks = re.compile(r'responded i-asks: (\d+)').search(statusData)
    parsedData['responded_i_asks'] = int(responded_i_asks.group(1)) if responded_i_asks else None

    searches = re.compile(r'searches: (\d+)').search(statusData)
    parsedData['searches'] = int(searches.group(1)) if searches else None

    open_sockettasks = re.compile(r'open sockettasks: (\d+)').search(statusData)
    parsedData['open_sockettasks'] = int(open_sockettasks.group(1)) if open_sockettasks else None

    return parsedData
