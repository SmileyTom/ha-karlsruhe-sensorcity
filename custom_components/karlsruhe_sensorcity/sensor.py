"""Sensor platform for Karlsruhe Sensor City."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPE_TEMPERATURE, SENSOR_TYPE_WIND
from .coordinator import SensorCityCoordinator


@dataclass(frozen=True, kw_only=True)
class SensorCityEntityDescription(SensorEntityDescription):
    attribute_key: str
    factor: float = 1.0


WIND_SENSORS: tuple[SensorCityEntityDescription, ...] = (
    SensorCityEntityDescription(
        key="wind_average_kmh",
        attribute_key="wind_average_kmh",
        name="Windgeschwindigkeit (Ø)",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorCityEntityDescription(
        key="wind_direction_degree",
        attribute_key="wind_direction_degree",
        name="Windrichtung",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:compass-rose",
        suggested_display_precision=0,
    ),
    SensorCityEntityDescription(
        key="windgust_1s_kmh",
        attribute_key="windgust_1s_kmh",
        name="Böenstärke (1 s)",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorCityEntityDescription(
        key="windgust_3s_kmh",
        attribute_key="windgust_3s_kmh",
        name="Böenstärke (3 s)",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
)

TEMPERATURE_SENSORS: tuple[SensorCityEntityDescription, ...] = (
    SensorCityEntityDescription(
        key="temp",
        attribute_key="temp",
        name="Temperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorCityEntityDescription(
        key="press",
        attribute_key="press",
        name="Luftdruck",
        native_unit_of_measurement=UnitOfPressure.PA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorCityEntityDescription(
        key="luftfeuchte",
        attribute_key="luftfeuchte",
        name="Luftfeuchte",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorCityEntityDescription(
        key="sonnenstrahlung",
        attribute_key="sonnenstrahlung",
        name="Sonnenstrahlung",
        native_unit_of_measurement="W/m²",
        device_class=SensorDeviceClass.IRRADIANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
)

SENSOR_MAP = {
    SENSOR_TYPE_WIND: WIND_SENSORS,
    SENSOR_TYPE_TEMPERATURE: TEMPERATURE_SENSORS,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SensorCityCoordinator = hass.data[DOMAIN][entry.entry_id]
    sensor_type = entry.data["sensor_type"]
    descriptions = SENSOR_MAP.get(sensor_type, ())

    async_add_entities(
        SensorCityEntity(coordinator, entry, desc)
        for desc in descriptions
        if coordinator.data.get(desc.attribute_key) is not None
    )


class SensorCityEntity(CoordinatorEntity[SensorCityCoordinator], SensorEntity):
    """One measurement from a Sensor City station."""

    entity_description: SensorCityEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SensorCityCoordinator,
        entry: ConfigEntry,
        description: SensorCityEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        station_name = entry.data["station_name"]
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry.entry_id)},
            name=station_name,
            manufacturer="Stadt Karlsruhe",
            model="Sensor City",
            configuration_url="https://geoportal.karlsruhe.de/sensorcity/Dashboard/",
        )

    @property
    def native_value(self) -> Any:
        raw = self.coordinator.data.get(self.entity_description.attribute_key)
        if raw is None:
            return None
        return round(float(raw) * self.entity_description.factor, 6)
