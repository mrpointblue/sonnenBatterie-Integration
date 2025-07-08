# File: custom_components/sonnenbatterie/sensor.py

from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
import aiohttp
import logging

from .const import DOMAIN, SENSORS, DEFAULT_PREFIX

_LOGGER = logging.getLogger(__name__)
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 5


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    ip = config_entry.data.get("ip_address")
    token = config_entry.data.get("token")
    custom_prefix = config_entry.data.get("custom_prefix", DEFAULT_PREFIX)

    scan_interval = (
        config_entry.options.get("scan_interval")
        or config_entry.data.get("scan_interval")
        or DEFAULT_SCAN_INTERVAL
    )

    scan_interval = max(scan_interval, MIN_SCAN_INTERVAL)

    coordinator = SonnenDataUpdateCoordinator(
        hass,
        _LOGGER,
        ip=ip,
        token=token,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    sensors = [
        SonnenBatterieSensor(coordinator, sensor, custom_prefix) for sensor in SENSORS
    ]
    async_add_entities(sensors)


class SonnenDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, logger, ip, token, update_interval):
        self.ip = ip
        self.token = token
        self.data_cache = {}
        super().__init__(
            hass,
            logger,
            name="SonnenDataUpdateCoordinator",
            update_method=self._async_update_data,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
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

        self.data_cache = results
        return results


class SonnenBatterieSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, sensor, custom_prefix):
        super().__init__(coordinator)
        self._name = f"{custom_prefix}_{sensor['name']}"
        self._key = sensor["key"]
        self._unit = sensor["unit"]
        self._device_class = sensor["device_class"]
        self._state_class = sensor.get("state_class")
        self._sensor_direction = sensor.get("direction")

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.coordinator.data_cache
        endpoint = self.determine_endpoint()

        if endpoint in data:
            endpoint_data = data[endpoint]
            if isinstance(endpoint_data, dict) and self._key in endpoint_data:
                value = endpoint_data[self._key]
                return round(value, 2) if isinstance(value, (int, float)) else value

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
        attributes = {}
        if self._state_class:
            attributes["state_class"] = self._state_class
        if self._sensor_direction:
            attributes["direction"] = self._sensor_direction
        return attributes

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def device_class(self):
        return self._device_class

    @property
    def state_class(self):
        return self._state_class

    @property
    def unique_id(self):
        direction_suffix = f"_{self._sensor_direction}" if self._sensor_direction else ""
        return f"{self._name}_{self.coordinator.ip}-{self._key}{direction_suffix}"

    def determine_endpoint(self):
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


# Update OptionsFlow to auto-reload after saving
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

class SonnenOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.entry,
                data={
                    "ip_address": user_input["ip_address"],
                    "token": user_input["token"],
                    "scan_interval": user_input["scan_interval"],
                    "custom_prefix": user_input.get("custom_prefix", DEFAULT_PREFIX),
                },
            )
            await self.hass.config_entries.async_reload(self.entry.entry_id)
            return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required("ip_address", default=self.entry.data["ip_address"]): cv.string,
                vol.Required("token", default=self.entry.data["token"]): cv.string,
                vol.Required("scan_interval", default=self.entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
                vol.Optional("custom_prefix", default=self.entry.data.get("custom_prefix", DEFAULT_PREFIX)): cv.string,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)