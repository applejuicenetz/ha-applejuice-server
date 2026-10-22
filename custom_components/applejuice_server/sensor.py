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
        key="cores",
        name="Cores",
        icon="mdi:account-group",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="user",
    ),
    AppleJuiceSensorDescription(
        key="cores_firewalled",
        name="Cores Firewalled",
        icon="mdi:account-off",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="firewalled",
    ),
    AppleJuiceSensorDescription(
        key="files",
        name="Files",
        icon="mdi:folder-file-outline",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="filecount",
    ),
    AppleJuiceSensorDescription(
        key="size",
        name="Size",
        icon="mdi:file-chart",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.TEBIBYTES,
        suggested_display_precision=2,
        data_key="filesize",
    ),
    AppleJuiceSensorDescription(
        key="connections",
        name="Connections",
        icon="mdi:connection",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="open_connections",
    ),
    AppleJuiceSensorDescription(
        key="memory_used",
        name="Memory used",
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="memory_used",
    ),
    AppleJuiceSensorDescription(
        key="memory_free",
        name="Memory free",
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="memory_free",
    ),
    AppleJuiceSensorDescription(
        key="memory_system",
        name="Memory system",
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
        key="sources",
        name="Sources",
        icon="mdi:source-branch",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="sended_sources",
    ),
    AppleJuiceSensorDescription(
        key="local_sources",
        name="Local sources",
        icon="mdi:source-branch",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="sended_local_sources",
    ),
    AppleJuiceSensorDescription(
        key="search_info",
        name="Search info",
        icon="mdi:comment-search",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="sended_searchmessages",
    ),
    AppleJuiceSensorDescription(
        key="indirect",
        name="Indirect",
        icon="mdi:message-alert",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="sended_firewallmessages",
    ),
    AppleJuiceSensorDescription(
        key="messages",
        name="Messages",
        icon="mdi:message",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="sended_messages",
    ),
    AppleJuiceSensorDescription(
        key="announcements",
        name="Announcements",
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
        key="tasks",
        name="Tasks",
        icon="mdi:transit-connection-variant",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        data_key="open_sockettasks",
    ),
)

SENSORS_NETWORK: tuple[AppleJuiceSensorDescription, ...] = (
    AppleJuiceSensorDescription(
        key="network_cores",
        name="Cores",
        icon="mdi:account-group",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="globaluser",
    ),
    AppleJuiceSensorDescription(
        key="network_files",
        name="Files",
        icon="mdi:file-document",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="globalfilecount",
    ),
    AppleJuiceSensorDescription(
        key="network_size",
        name="Size",
        icon="mdi:file-document-outline",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.TEBIBYTES,
        suggested_display_precision=2,
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
