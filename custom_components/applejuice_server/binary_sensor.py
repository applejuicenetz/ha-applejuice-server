"""Binary sensors platform for appleJuice Server integration."""
import logging
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import DOMAIN
from .entity import BaseAppleJuiceServerEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class AppleJuiceServerBinarySensorDescription(BinarySensorEntityDescription):
    """Class describing appleJuice Server binary_sensor entities."""

    key: str
    name: str
    sensor_name: str | None = None
    subscriptions: list | None = None
    icon: str | None = None
    device_class: str | None = None
    entity_category: str | None = None


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    await async_setup_update_binary_sensors(coordinator, entry, async_add_devices)


async def async_setup_update_binary_sensors(coordinator, entry, async_add_entities):
    """Set Machine Update binary sensor."""

    desc = AppleJuiceServerBinarySensorDescription(
        key="serverstatus_ok",
        sensor_name="serverstatus",
        name="Server Status",
        icon="mdi:gauge-full",
        device_class=BinarySensorDeviceClass.PROBLEM,
        subscriptions=[("serverstatus_ok")],
    )

    await coordinator.async_refresh()

    async_add_entities([AppleJuiceServerBinarySensor(coordinator, entry, desc)])


class AppleJuiceServerBinarySensor(BaseAppleJuiceServerEntity, BinarySensorEntity):
    """appleJuice Server binary_sensor class."""

    def __init__(
            self,
            coordinator,
            entry,
            description,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        self.sensor_name = description.sensor_name
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_has_entity_name = True
        self._attr_icon = description.icon
        self._coordinator = coordinator

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        return self._coordinator.data.get(self.entity_description.key) != True
