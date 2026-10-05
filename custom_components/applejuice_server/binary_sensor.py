"""Binary sensor platform for the appleJuice Server integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AppleJuiceConfigEntry
from .entity import AppleJuiceServerEntity

PARALLEL_UPDATES = 0

DESCRIPTION = BinarySensorEntityDescription(
    key="serverstatus_ok",
    name="Server Status",
    icon="mdi:gauge-full",
    device_class=BinarySensorDeviceClass.PROBLEM,
)


class AppleJuiceServerStatus(AppleJuiceServerEntity, BinarySensorEntity):
    """Problem sensor: on when the server reports that it is full."""

    @property
    def is_on(self) -> bool | None:
        """True if the server health is not ok, None if unknown."""
        ok = self.coordinator.data.get("serverstatus_ok")
        return None if ok is None else not ok


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AppleJuiceConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary sensor platform."""
    async_add_entities([AppleJuiceServerStatus(entry.runtime_data, DESCRIPTION)])
