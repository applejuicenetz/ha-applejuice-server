"""Base class entity for appleJuice Server."""
import logging

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class BaseAppleJuiceServerEntity(CoordinatorEntity):
    """Base class entity for appleJuice Server."""

    def __init__(self, coordinator, config_entry):
        """Init."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._name = coordinator.name

    @property
    def device_info(self):
        """Entity device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            name=self._name,
            model="appleJuice Server",
            manufacturer="appleJuiceNETZ",
            entry_type=DeviceEntryType.SERVICE,
        )


class BaseAppleJuiceNetworkEntity(CoordinatorEntity):
    """Base class entity for appleJuice Network."""

    def __init__(self, coordinator, config_entry):
        """Init."""
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def device_info(self):
        """Entity device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.entry_id, "network")},
            name="appleJuice Network",
            model="appleJuice Network",
            manufacturer="appleJuiceNETZ",
            entry_type=DeviceEntryType.SERVICE,
        )
