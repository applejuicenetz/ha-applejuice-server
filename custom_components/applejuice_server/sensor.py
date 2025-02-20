import logging
from dataclasses import dataclass
from collections.abc import Callable
from datetime import datetime

from homeassistant.const import (
    EntityCategory,
    UnitOfInformation,
    UnitOfDataRate,
)

from homeassistant.core import callback

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from .const import DOMAIN
from .entity import BaseAppleJuiceServerEntity, BaseAppleJuiceNetworkEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class AppleJuiceServerSensorDescription(SensorEntityDescription):
    """Class describing appleJuice Server sensor entities."""

    key: str
    name: str
    value_fn: Callable | None = None
    sensor_name: str | None = None
    icon: str | None = None
    unit: str | None = None
    state_class: str | None = None
    device_class: str | None = None
    subscriptions: list | None = None
    entity_category: str | None = None


SENSORS_SERVER: tuple[AppleJuiceServerSensorDescription, ...] = [
    AppleJuiceServerSensorDescription(
        key="users",
        name="Users",
        icon="mdi:account-group",
        state_class=SensorStateClass.TOTAL,
        subscriptions=[("user")],
        value_fn=lambda sensor: sensor.coordinator.data.get("user"),
    ),
    AppleJuiceServerSensorDescription(
        key="users_firewalled",
        name="Users Firewalled",
        icon="mdi:account-off",
        state_class=SensorStateClass.TOTAL,
        subscriptions=[("firewalled")],
        value_fn=lambda sensor: sensor.coordinator.data.get("firewalled"),
    ),
    AppleJuiceServerSensorDescription(
        key="filecount",
        name="File Count",
        icon="mdi:folder-file-outline",
        state_class=SensorStateClass.TOTAL,
        subscriptions=[("filecount")],
        value_fn=lambda sensor: sensor.coordinator.data.get("filecount"),
    ),
    AppleJuiceServerSensorDescription(
        key="filesize",
        name="File Size",
        icon="mdi:file-chart",
        state_class=SensorStateClass.TOTAL,
        unit=UnitOfInformation.TERABYTES,
        subscriptions=[("filesize")],
        value_fn=lambda sensor: sensor.coordinator.data.get("filesize") / (1024 ** 4),
    ),
    AppleJuiceServerSensorDescription(
        key="open_connections",
        name="Open Connections",
        icon="mdi:connection",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorStateClass.TOTAL,
        subscriptions=[("open_connections")],
        value_fn=lambda sensor: sensor.coordinator.data.get("open_connections"),
    ),
    AppleJuiceServerSensorDescription(
        key="memory used",
        name="Memory Used",
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorStateClass.TOTAL,
        unit=UnitOfInformation.KILOBYTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("memory_used")],
        value_fn=lambda sensor: sensor.coordinator.data.get("memory_used"),
    ),
    AppleJuiceServerSensorDescription(
        key="memory_free",
        name="Memory Free",
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorStateClass.TOTAL,
        unit=UnitOfInformation.KILOBYTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("memory_free")],
        value_fn=lambda sensor: sensor.coordinator.data.get("memory_free"),
    ),
    AppleJuiceServerSensorDescription(
        key="memory max",
        name="Memory Max",
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorStateClass.TOTAL,
        unit=UnitOfInformation.KILOBYTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("memory_max")],
        value_fn=lambda sensor: sensor.coordinator.data.get("memory_max"),
    ),
    AppleJuiceServerSensorDescription(
        key="upspeed_last_10_sec",
        name="Upload Speed Last 10 Sec",
        icon="mdi:upload-network",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorStateClass.TOTAL,
        unit=UnitOfDataRate.KILOBYTES_PER_SECOND,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("upspeed_last_10_sec")],
        value_fn=lambda sensor: sensor.coordinator.data.get("upspeed_last_10_sec"),
    ),
    AppleJuiceServerSensorDescription(
        key="downspeed_last_10_sec",
        name="Download Speed Last 10 Sec",
        icon="mdi:download-network",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorStateClass.TOTAL,
        unit=UnitOfDataRate.KILOBYTES_PER_SECOND,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("downspeed_last_10_sec")],
        value_fn=lambda sensor: sensor.coordinator.data.get("downspeed_last_10_sec"),
    ),
    AppleJuiceServerSensorDescription(
        key="sended_sources",
        name="Sended Sources",
        icon="mdi:source-branch",
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("sended_sources")],
        value_fn=lambda sensor: sensor.coordinator.data.get("sended_sources"),
    ),
    AppleJuiceServerSensorDescription(
        key="sended_local_sources",
        name="Sended Local Sources",
        icon="mdi:source-branch",
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("sended_local_sources")],
        value_fn=lambda sensor: sensor.coordinator.data.get("sended_local_sources"),
    ),
    AppleJuiceServerSensorDescription(
        key="sended_searchmessages",
        name="Sended Search Messages",
        icon="mdi:message-search",
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("sended_searchmessages")],
        value_fn=lambda sensor: sensor.coordinator.data.get("sended_searchmessages"),
    ),
    AppleJuiceServerSensorDescription(
        key="sended_firewallmessages",
        name="Sended Firewall Messages",
        icon="mdi:message-alert",
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("sended_firewallmessages")],
        value_fn=lambda sensor: sensor.coordinator.data.get("sended_firewallmessages"),
    ),
    AppleJuiceServerSensorDescription(
        key="sended_messages",
        name="Sended Messages",
        icon="mdi:message",
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("sended_messages")],
        value_fn=lambda sensor: sensor.coordinator.data.get("sended_messages"),
    ),
    AppleJuiceServerSensorDescription(
        key="messagesize",
        name="Message Size",
        icon="mdi:message-text",
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("messagesize")],
        value_fn=lambda sensor: sensor.coordinator.data.get("messagesize"),
    ),
    AppleJuiceServerSensorDescription(
        key="responded_i_asks",
        name="Responded I-Asks",
        icon="mdi:message-reply",
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("responded_i_asks")],
        value_fn=lambda sensor: sensor.coordinator.data.get("responded_i_asks"),
    ),
    AppleJuiceServerSensorDescription(
        key="searches",
        name="Searches",
        icon="mdi:magnify",
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("searches")],
        value_fn=lambda sensor: sensor.coordinator.data.get("searches"),
    ),
    AppleJuiceServerSensorDescription(
        key="open_sockettasks",
        name="Open Socket Tasks",
        icon="mdi:socket",
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        subscriptions=[("open_sockettasks")],
        value_fn=lambda sensor: sensor.coordinator.data.get("open_sockettasks"),
    )
]

SENSORS_NETWORK: tuple[AppleJuiceServerSensorDescription, ...] = [
    AppleJuiceServerSensorDescription(
        key="globaluser",
        name="Global Users",
        icon="mdi:account-group",
        state_class=SensorStateClass.TOTAL,
        subscriptions=[("globaluser")],
        value_fn=lambda sensor: sensor.coordinator.data.get("globaluser"),
    ),
    AppleJuiceServerSensorDescription(
        key="globalfilecount",
        name="Global File Count",
        icon="mdi:file-document",
        state_class=SensorStateClass.TOTAL,
        subscriptions=[("globalfilecount")],
        value_fn=lambda sensor: sensor.coordinator.data.get("globalfilecount"),
    ),
    AppleJuiceServerSensorDescription(
        key="globalfilesize",
        name="Global File Size",
        icon="mdi:file-document-outline",
        unit=UnitOfInformation.TERABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        subscriptions=[("globalfilesize")],
        value_fn=lambda sensor: round(sensor.coordinator.data.get("globalfilesize") / (1024 ** 4), 2),
    ),
]


async def async_setup_entry(hass, entry, async_add_entities):
    """Set sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    await async_setup_basic_sensor(coordinator, entry, async_add_entities)


async def async_setup_basic_sensor(coordinator, entry, async_add_entities):
    """Set basic sensor platform."""
    async_add_entities(
        [AppleJuiceServerSensor(coordinator, entry, desc) for desc in SENSORS_SERVER] +
        [AppleJuiceNetworkSensor(coordinator, entry, desc) for desc in SENSORS_NETWORK]
    )


class AppleJuiceServerSensor(BaseAppleJuiceServerEntity, SensorEntity):
    """AppleJuiceServerSensor Sensor class."""

    def __init__(self, coordinator, entry, description):
        """Init."""
        super().__init__(coordinator, entry)
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_has_entity_name = True
        self.entity_description = description
        self._attr_native_value = description.value_fn(self)
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.unit

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.entity_description.value_fn(self)
        self.async_write_ha_state()


class AppleJuiceNetworkSensor(BaseAppleJuiceNetworkEntity, SensorEntity):
    """AppleJuiceNetworkSensor Sensor class."""

    def __init__(self, coordinator, entry, description):
        """Init."""
        super().__init__(coordinator, entry)
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_has_entity_name = True
        self.entity_description = description
        self._attr_native_value = description.value_fn(self)
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.unit

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.entity_description.value_fn(self)
        self.async_write_ha_state()
