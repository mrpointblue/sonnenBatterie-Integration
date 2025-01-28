from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
import aiohttp
import logging

from .const import DOMAIN, SENSORS, DEFAULT_PREFIX

_LOGGER = logging.getLogger(__name__)
DEFAULT_SCAN_INTERVAL = 30  # Default in Sekunden
MIN_SCAN_INTERVAL = 5  # Minimum in Sekunden


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """
    Asynchronous setup of sonnenbatterie sensors based on config entry.
    """
    ip = config_entry.data["ip_address"]
    token = config_entry.data["token"]
    scan_interval = config_entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    custom_prefix = config_entry.data.get("custom_prefix", DEFAULT_PREFIX)

    coordinator = SonnenDataUpdateCoordinator(
        hass,
        _LOGGER,
        ip=ip,
        token=token,
        update_interval=timedelta(seconds=max(scan_interval, MIN_SCAN_INTERVAL)),
    )

    await coordinator.async_config_entry_first_refresh()

    sensors = [
        SonnenBatterieSensor(coordinator, sensor, custom_prefix) for sensor in SENSORS
    ]
    async_add_entities(sensors)


class SonnenDataUpdateCoordinator(DataUpdateCoordinator):
    """Custom DataUpdateCoordinator to manage fetching data from multiple API endpoints."""

    def __init__(self, hass, logger, ip, token, update_interval):
        """Initialize the data update coordinator."""
        self.ip = ip
        self.token = token
        self.data_cache = {}  # Cache for data from multiple endpoints
        super().__init__(
            hass,
            logger,
            name="SonnenDataUpdateCoordinator",
            update_method=self._async_update_data,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from the Sonnen API."""
        headers = {
            "User-Agent": "Home Assistant",
            "Content-Type": "application/json",
            "Auth-Token": self.token,
        }

        endpoints = [
            "/api/v2/inverter",
            "/api/v2/status",
            "/api/v2/configurations",
            "/api/v2/battery",
            "/api/v2/powermeter",
            "/api/v2/latestdata",
        ]

        results = {}
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    url = f"http://{self.ip}{endpoint}"
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            results[endpoint] = data
                        else:
                            _LOGGER.warning(f"Failed to fetch data from {endpoint}: {response.status}")
                except Exception as e:
                    _LOGGER.error(f"Error fetching data from {endpoint}: {e}")

        self.data_cache = results  # Store the fetched data
        return results


class SonnenBatterieSensor(CoordinatorEntity, Entity):
    """Representation of a Sonnenbatterie sensor."""

    def __init__(self, coordinator, sensor, custom_prefix):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = f"{custom_prefix}_{sensor['name']}"
        self._key = sensor["key"]
        self._unit = sensor["unit"]
        self._device_class = sensor["device_class"]
        self._state_class = sensor.get("state_class")
        self._sensor_direction = sensor.get("direction")

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state of the sensor."""
        data = self.coordinator.data_cache
        endpoint = self.determine_endpoint()

        if endpoint in data:
            endpoint_data = data[endpoint]
            if isinstance(endpoint_data, dict) and self._key in endpoint_data:
                return round(endpoint_data[self._key], 2) if isinstance(endpoint_data[self._key], (int, float)) else endpoint_data[self._key]
            if isinstance(endpoint_data, list):
                for entry in endpoint_data:
                    if (
                        self._sensor_direction
                        and entry.get("direction") == self._sensor_direction
                        and self._key in entry
                    ):
                        value = entry[self._key]
                        return round(value, 2) if isinstance(value, (int, float)) else value
        return None

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes of the sensor."""
        attributes = {}
        if self._state_class:
            attributes["state_class"] = self._state_class
        if self._sensor_direction:
            attributes["direction"] = self._sensor_direction
        return attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement for the sensor."""
        return self._unit

    @property
    def device_class(self):
        """Return the device class for the sensor."""
        return self._device_class

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return self._state_class

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        direction_suffix = f"_{self._sensor_direction}" if self._sensor_direction else ""
        return f"{self._name}_{self.coordinator.ip}-{self._key}{direction_suffix}"

    def determine_endpoint(self):
        """
        Determine the correct API endpoint based on the sensor key.
        """
        if self._key in [
            "fac", "iac_total", "ibat", "ipv", "pac_microgrid", "pac_total", "pbat", "phi", "ppv", "sac_total", "tmax", "uac", "upv"
        ]:
            return "/api/v2/inverter"
        if self._key in [
            "Apparent_output", "BackupBuffer", "BatteryCharging", "BatteryDischarging",
            "Consumption_W", "Fac", "FlowConsumptionBattery", "FlowConsumptionGrid",
            "FlowConsumptionProduction", "FlowGridBattery", "FlowProductionBattery",
            "FlowProductionGrid", "GridFeedIn_W", "IsSystemInstalled", "OperatingMode",
            "Pac_total_W", "Production_W", "RSOC", "SystemStatus", "Timestamp",
            "Uac", "Ubat", "dischargeNotAllowed", "generator_autostart"
        ]:
            return "/api/v2/status"
        if self._key in [
            "EM_OperatingMode", "IC_InverterMaxPower_w", "IC_BatteryModules", "NVM_PfcFixedCosPhi",
            "CM_MarketingModuleCapacity", "CN_CascadingRole", "DE_Software",
        ]:
            return "/api/v2/configurations"
        if self._key in [
            "BatteryVoltage", "cyclecount", "BackupBuffer", "fullchargecapacity", "remainingcapacity",
            "systemdcvoltage", "systemcurrent", "maximumcelltemperature", "minimumcelltemperature",
            "maximumcellvoltage", "minimumcellvoltage", "maximummoduledcvoltage",
            "minimummoduledcvoltage", "chargecurrentlimit", "dischargecurrentlimit",
            "systemstatus", "systemwarning"
        ]:
            return "/api/v2/battery"
        if self._key in [
            "va_total", "var_total", "w_l1", "w_l2", "w_l3", "w_total",
            "a_l1", "a_l2", "a_l3", "v_l1_n", "v_l2_n", "v_l3_n",
            "v_l1_l2", "v_l2_l3", "v_l3_l1", "kwh_exported", "kwh_imported",
        ]:
            return "/api/v2/powermeter"
        return "/api/v2/latestdata"
