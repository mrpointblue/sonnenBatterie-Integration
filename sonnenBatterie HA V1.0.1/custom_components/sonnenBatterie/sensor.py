from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
import aiohttp
import logging

from .const import DOMAIN, SENSORS, DEFAULT_PREFIX

_LOGGER = logging.getLogger(__name__)
DEFAULT_SCAN_INTERVAL = 30  # Default in Sekunden
MIN_SCAN_INTERVAL = 5  # Minimum in Sekunden

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """
    Asynchronous setup of sonnenBatterie sensors based on config entry.
    """
    ip = config_entry.data["ip_address"]
    token = config_entry.data["token"]
    scan_interval = config_entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    custom_prefix = config_entry.data.get("custom_prefix", DEFAULT_PREFIX)
    entities = [
        SonnenBatterieSensor(sensor, ip, token, scan_interval, custom_prefix) for sensor in SENSORS
    ]
    async_add_entities(entities, update_before_add=True)

class SonnenBatterieSensor(Entity):
    """Representation of a SonnenBatterie sensor."""

    def __init__(self, sensor, ip, token, scan_interval, custom_prefix):
        """
        Initialize the sensor.
        """
        self._name = f"{custom_prefix}_{sensor['name']}"
        self._key = sensor["key"]
        self._unit = sensor["unit"]
        self._device_class = sensor["device_class"]
        self._state_class = sensor.get("state_class")
        self._sensor_direction = sensor.get("direction")
        self._state = None
        self._ip = ip
        self._token = token
        self._scan_interval = max(scan_interval, MIN_SCAN_INTERVAL)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

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
    def state(self):
        """Return the current state of the sensor."""
        return self._state

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
        """Return a unique ID for the sensor based on its key, direction, and IP address."""
        direction_suffix = f"_{self._sensor_direction}" if self._sensor_direction else ""
        return f"{self._name}_{self._ip}-{self._key}{direction_suffix}"

    async def async_update(self):
        """
        Asynchronous update logic for fetching data from the appropriate endpoint.
        """
        headers = {
            "User-Agent": "Home Assistant",
            "Content-Type": "application/json",
            "Auth-Token": self._token,
        }

        try:
            # Determine the correct API endpoint for the sensor
            url = self.determine_endpoint()

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.warning(f"Error fetching data for {self._name}: {response.status}")
                        self._state = None
                        return

                    data = await response.json()
                    _LOGGER.debug(f"API response for {self._name}: {data}")

            # Process powermeter data with direction filtering
            if url.endswith("/powermeter"):
                for entry in data:
                    _LOGGER.debug(f"Processing powermeter entry: {entry}")
                    if (
                        self._sensor_direction
                        and entry.get("direction") == self._sensor_direction
                        and self._key in entry
                    ):
                        value = entry[self._key]
                        self._state = round(value, 2) if isinstance(value, (int, float)) else value
                        return
                _LOGGER.warning(
                    f"Key '{self._key}' or direction '{self._sensor_direction}' not found in powermeter data for {self._name}."
                )
                self._state = None
                return

            # Handle nested keys (e.g., "ic_status.stateinverter")
            else:
                keys = self._key.split(".")
                value = data
                for key in keys:
                    value = value.get(key, None)
                    if value is None:
                        break
                if value is not None:
                    self._state = round(value, 2) if isinstance(value, (int, float)) else value
                else:
                    _LOGGER.warning(f"Key '{self._key}' not found in API response for sensor '{self._name}'.")

        except Exception as e:
            self._state = None
            _LOGGER.error(f"Error updating {self._name}: {e}")

    def determine_endpoint(self):
        """
        Determine the correct API endpoint based on the sensor key.
        """
        # /api/v2/inverter
        if self._key in [
            "fac", "iac_total", "ibat", "ipv", "pac_microgrid", "pac_total", "pbat", "phi", "ppv", "sac_total", "tmax", "uac", "upv"
        ]:
            return f"http://{self._ip}/api/v2/inverter"

        # /api/v2/status
        if self._key in [
            "Apparent_output", "BackupBuffer", "BatteryCharging", "BatteryDischarging",
            "Consumption_W", "Fac", "FlowConsumptionBattery", "FlowConsumptionGrid",
            "FlowConsumptionProduction", "FlowGridBattery", "FlowProductionBattery",
            "FlowProductionGrid", "GridFeedIn_W", "IsSystemInstalled", "OperatingMode",
            "Pac_total_W", "Production_W", "RSOC", "SystemStatus", "Timestamp",
            "Uac", "Ubat", "dischargeNotAllowed", "generator_autostart"
        ]:
            return f"http://{self._ip}/api/v2/status"

        # /api/v2/configurations
        if self._key in [
            "EM_OperatingMode", "IC_InverterMaxPower_w", "IC_BatteryModules", "NVM_PfcFixedCosPhi",
            "CM_MarketingModuleCapacity", "CN_CascadingRole", "DE_Software",
        ]:
            return f"http://{self._ip}/api/v2/configurations"

        # /api/v2/battery
        if self._key in [
            "BatteryVoltage", "cyclecount", "BackupBuffer", "fullchargecapacity", "remainingcapacity",
            "systemdcvoltage", "systemcurrent", "maximumcelltemperature", "minimumcelltemperature",
            "maximumcellvoltage", "minimumcellvoltage", "maximummoduledcvoltage",
            "minimummoduledcvoltage", "chargecurrentlimit", "dischargecurrentlimit",
            "systemstatus", "systemwarning"
        ]:
            return f"http://{self._ip}/api/v2/battery"

        # /api/v2/powermeter
        if self._key in [
            "va_total", "var_total", "w_l1", "w_l2", "w_l3", "w_total",
            "a_l1", "a_l2", "a_l3", "v_l1_n", "v_l2_n", "v_l3_n",
            "v_l1_l2", "v_l2_l3", "v_l3_l1", "kwh_exported", "kwh_imported",
        ]:
            return f"http://{self._ip}/api/v2/powermeter"

        # /api/v2/latestdata
        if self._key in [
            "Consumption_W", "FullChargeCapacity", "Production_W", "GridFeedIn_W", "USOC", "Pac_total_W",
        ]:
            return f"http://{self._ip}/api/v2/latestdata"

        # Default fallback for unknown keys
        else:
            return f"http://{self._ip}/api/v2/latestdata"