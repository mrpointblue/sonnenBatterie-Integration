"""Sensors and coordinated local polling for sonnenBatterie."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SENSORS, DEFAULT_PREFIX
from .coordinator import SonnenDataUpdateCoordinator

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    config = {**config_entry.data, **config_entry.options}
    coordinator = config_entry.runtime_data
    async_add_entities([
        SonnenBatterieSensor(coordinator, sensor, config.get("custom_prefix", DEFAULT_PREFIX))
        for sensor in SENSORS
    ])

class SonnenBatterieSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sensor, custom_prefix):
        super().__init__(coordinator)
        self._key = sensor["key"]
        self._path = sensor.get("path", [self._key])
        self._flags = sensor.get("flags", False)
        if sensor.get("diagnostic"):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
            self._attr_entity_registry_enabled_default = False
        self._endpoint = sensor["endpoint"]
        self._direction = sensor.get("direction")
        self._attr_name = f"{custom_prefix}_{sensor['name']}"
        self._attr_native_unit_of_measurement = sensor["unit"]
        self._attr_device_class = sensor["device_class"]
        self._attr_state_class = sensor.get("state_class")
        self._attr_has_entity_name = True
        suffix = f"_{self._direction}" if self._direction else ""
        self._attr_unique_id = (
            f"{coordinator.identity_prefix}_{sensor['name']}_"
            f"{coordinator.identity_ip}-{self._key}{suffix}"
        )
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.identity_ip)},
            "name": f"SonnenBatterie {coordinator.ip}",
            "manufacturer": "Sonnen", "model": "SonnenBatterie",
        }

    @property
    def available(self):
        return (super().available
                and self._endpoint in (self.coordinator.data or {})
                and self._raw_value() is not None)

    def _raw_value(self):
        data = (self.coordinator.data or {}).get(self._endpoint)
        if isinstance(data, list):
            data = next((item for item in data if isinstance(item, dict)
                         and item.get("direction") == self._direction), {})
        for key in self._path:
            data = data.get(key) if isinstance(data, dict) else None
        return data

    @property
    def native_value(self):
        value = self._raw_value()
        if self._flags:
            return sum(flag is True for flag in value.values()) if isinstance(value, dict) else None
        if self._attr_device_class == "timestamp":
            if not isinstance(value, str):
                return None
            try:
                parsed = dt_util.parse_datetime(value)
            except ValueError:
                return None
            # Do not invent a timezone for an ambiguous device timestamp.
            return parsed if parsed and parsed.tzinfo else None
        if isinstance(value, bool):
            return int(value)
        return value

    @property
    def extra_state_attributes(self):
        if self._flags:
            value = self._raw_value()
            return {"flags": value} if isinstance(value, dict) else None
        return {"direction": self._direction} if self._direction else None
