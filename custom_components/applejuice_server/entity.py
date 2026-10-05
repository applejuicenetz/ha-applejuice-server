"""Base entities for the appleJuice Server integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AppleJuiceCoordinator


class AppleJuiceServerEntity(CoordinatorEntity[AppleJuiceCoordinator]):
    """Entity attached to the appleJuice Server device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AppleJuiceCoordinator, description: EntityDescription) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Device of the Server."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=self.coordinator.name,
            sw_version=self.coordinator.version,
            model="appleJuice Server",
            manufacturer="appleJuiceNETZ",
            entry_type=DeviceEntryType.SERVICE,
        )


class AppleJuiceNetworkEntity(AppleJuiceServerEntity):
    """Entity attached to the appleJuice Network device."""

    @property
    def device_info(self) -> DeviceInfo:
        """Device of the Network (linked to the Server device in __init__)."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.coordinator.config_entry.entry_id}_network")},
            name="appleJuice Network",
            model="appleJuice Network",
            manufacturer="appleJuiceNETZ",
            entry_type=DeviceEntryType.SERVICE,
        )
