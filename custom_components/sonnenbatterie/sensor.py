"""Sensors and coordinated local polling for sonnenBatterie."""
import asyncio
from datetime import timedelta
import logging
import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SENSORS, DEFAULT_PREFIX, DEFAULT_SCAN_INTERVAL, MIN_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    config = {**config_entry.data, **config_entry.options}
    coordinator = SonnenDataUpdateCoordinator(hass, config_entry, config)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([
        SonnenBatterieSensor(coordinator, sensor, config.get("custom_prefix", DEFAULT_PREFIX))
        for sensor in SENSORS
    ])

class SonnenDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, config):
        self.ip = config["ip_address"]
        self.token = config["token"]
        self.identity_ip = entry.data["identity_ip"]
        self.identity_prefix = entry.data["identity_prefix"]
        self.session = async_get_clientsession(hass)
        super().__init__(
            hass, _LOGGER, name=DOMAIN, config_entry=entry,
            update_interval=timedelta(seconds=max(
                config.get("scan_interval", DEFAULT_SCAN_INTERVAL), MIN_SCAN_INTERVAL)),
        )

    async def _async_update_data(self):
        async def fetch(endpoint):
            try:
                async with self.session.get(
                    f"http://{self.ip}{endpoint}",
                    headers={"Auth-Token": self.token},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status in (401, 403):
                        raise ConfigEntryAuthFailed("Invalid sonnenBatterie token or API permissions")
                    response.raise_for_status()
                    data = await response.json()
                    expected = list if endpoint.endswith("/powermeter") else dict
                    if not isinstance(data, expected) or not data:
                        raise ValueError("Empty or unexpected response")
                    return endpoint, data
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
                _LOGGER.debug("Could not fetch %s: %s", endpoint, err)
                return endpoint, None

        responses = await asyncio.gather(*(fetch(endpoint) for endpoint in
            sorted({sensor["endpoint"] for sensor in SENSORS})))
        results = {endpoint: data for endpoint, data in responses if data is not None}
        if not results:
            raise UpdateFailed("No sonnenBatterie API endpoint could be read")
        return results

class SonnenBatterieSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sensor, custom_prefix):
        super().__init__(coordinator)
        self._key = sensor["key"]
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
        return super().available and self._endpoint in (self.coordinator.data or {})

    @property
    def native_value(self):
        data = (self.coordinator.data or {}).get(self._endpoint)
        if isinstance(data, list):
            data = next((item for item in data if isinstance(item, dict)
                         and item.get("direction") == self._direction), {})
        value = data.get(self._key) if isinstance(data, dict) else None
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
        return {"direction": self._direction} if self._direction else None
