"""Sensor platform for the appleJuice Server integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfDataRate, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AppleJuiceConfigEntry
from .entity import AppleJuiceNetworkEntity, AppleJuiceServerEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class AppleJuiceSensorDescription(SensorEntityDescription):
    """Describes an appleJuice Server sensor."""

    data_key: str


SENSORS_SERVER: tuple[AppleJuiceSensorDescription, ...] = (
    AppleJuiceSensorDescription(
        key="users",
        name="Users",
        icon="mdi:account-group",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="user",
    ),
    AppleJuiceSensorDescription(
        key="users_firewalled",
        name="Users Firewalled",
        icon="mdi:account-off",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="firewalled",
    ),
    AppleJuiceSensorDescription(
        key="filecount",
        name="File Count",
        icon="mdi:folder-file-outline",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="filecount",
    ),
    AppleJuiceSensorDescription(
        key="filesize",
        name="File Size",
        icon="mdi:file-chart",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        data_key="filesize",
    ),
    AppleJuiceSensorDescription(
        key="open_connections",
        name="Open Connections",
        icon="mdi:connection",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="open_connections",
    ),
    AppleJuiceSensorDescription(
        key="memory used",
        name="Memory Used",
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="memory_used",
    ),
    AppleJuiceSensorDescription(
        key="memory_free",
        name="Memory Free",
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="memory_free",
    ),
    AppleJuiceSensorDescription(
        key="memory max",
        name="Memory Max",
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="memory_max",
    ),
    AppleJuiceSensorDescription(
        key="upspeed_last_10_sec",
        name="Upload Speed Last 10 Sec",
        icon="mdi:upload-network",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="upspeed_last_10_sec",
    ),
    AppleJuiceSensorDescription(
        key="downspeed_last_10_sec",
        name="Download Speed Last 10 Sec",
        icon="mdi:download-network",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="downspeed_last_10_sec",
    ),
    AppleJuiceSensorDescription(
        key="sended_sources",
        name="Sended Sources",
        icon="mdi:source-branch",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="sended_sources",
    ),
    AppleJuiceSensorDescription(
        key="sended_local_sources",
        name="Sended Local Sources",
        icon="mdi:source-branch",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="sended_local_sources",
    ),
    AppleJuiceSensorDescription(
        key="sended_searchmessages",
        name="Sended Search Messages",
        icon="mdi:comment-search",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="sended_searchmessages",
    ),
    AppleJuiceSensorDescription(
        key="sended_firewallmessages",
        name="Sended Firewall Messages",
        icon="mdi:message-alert",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="sended_firewallmessages",
    ),
    AppleJuiceSensorDescription(
        key="sended_messages",
        name="Sended Messages",
        icon="mdi:message",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="sended_messages",
    ),
    AppleJuiceSensorDescription(
        key="messagesize",
        name="Message Size",
        icon="mdi:message-text",
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="messagesize",
    ),
    AppleJuiceSensorDescription(
        key="responded_i_asks",
        name="Responded I-Asks",
        icon="mdi:message-reply",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="responded_i_asks",
    ),
    AppleJuiceSensorDescription(
        key="searches",
        name="Searches",
        icon="mdi:magnify",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="searches",
    ),
    AppleJuiceSensorDescription(
        key="open_sockettasks",
        name="Open Socket Tasks",
        icon="mdi:transit-connection-variant",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="open_sockettasks",
    ),
)

SENSORS_NETWORK: tuple[AppleJuiceSensorDescription, ...] = (
    AppleJuiceSensorDescription(
        key="globaluser",
        name="Global Users",
        icon="mdi:account-group",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="globaluser",
    ),
    AppleJuiceSensorDescription(
        key="globalfilecount",
        name="Global File Count",
        icon="mdi:file-document",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="globalfilecount",
    ),
    AppleJuiceSensorDescription(
        key="globalfilesize",
        name="Global File Size",
        icon="mdi:file-document-outline",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        data_key="globalfilesize",
    ),
)


class AppleJuiceServerSensor(AppleJuiceServerEntity, SensorEntity):
    """Sensor of the Server device."""

    entity_description: AppleJuiceSensorDescription

    @property
    def native_value(self) -> int | None:
        """Current value."""
        return self.coordinator.data.get(self.entity_description.data_key)


class AppleJuiceNetworkSensor(AppleJuiceNetworkEntity, AppleJuiceServerSensor):
    """Sensor of the Network device."""


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AppleJuiceConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator = entry.runtime_data
    async_add_entities(
        [AppleJuiceServerSensor(coordinator, desc) for desc in SENSORS_SERVER]
        + [AppleJuiceNetworkSensor(coordinator, desc) for desc in SENSORS_NETWORK]
    )
