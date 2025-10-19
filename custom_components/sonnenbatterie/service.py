import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .battery_control import (
    set_em_operating_mode,
    set_battery_power,
    get_system_status,
    restart_battery,
)

_LOGGER = logging.getLogger(__name__)

DOMAIN = "sonnenbatterie"

async def async_register_services(hass: HomeAssistant, config: dict, ip: str, token: str):
    """Registriert die sonnenbatterie-Services in Home Assistant."""

    async def handle_set_battery_power(call: ServiceCall):
        direction = call.data.get("direction")
        watts = call.data.get("watts", 1000)
        if direction not in ["charge", "discharge"] or watts < 0:
            _LOGGER.error(f"Ungültige Parameter: {direction}, {watts}")
            return
        success = await set_battery_power(ip, token, direction, watts)
        if success:
            _LOGGER.info(f"Batterieleistung gesetzt: {direction} {watts}W")
        else:
            _LOGGER.error("Fehler beim Setzen der Leistung")

    async def handle_set_em_operating_mode(call: ServiceCall):
        mode = call.data.get("mode", 2)
        success = await set_em_operating_mode(ip, token, mode)
        if success:
            _LOGGER.info(f"Modus gesetzt: {mode}")
        else:
            _LOGGER.error(f"Fehler beim Setzen des Modus: {mode}")

    async def handle_get_system_status(call: ServiceCall):
        include_raw = call.data.get("include_raw", False)
        _LOGGER.debug("Systemstatus wird abgerufen...")
        status = await get_system_status(ip, token, include_raw=include_raw)
        if status:
            _LOGGER.info(f"Aktueller Status: {status}")
        else:
            _LOGGER.error("Fehler beim Abrufen des Status")

    async def handle_restart_battery(call: ServiceCall):
        confirm = call.data.get("confirm", False)
        if not confirm:
            _LOGGER.warning("Neustart wurde nicht bestätigt – Vorgang abgebrochen.")
            return
        success = await restart_battery(ip, token)
        if success:
            _LOGGER.info("Batterie-System wurde neugestartet.")
        else:
            _LOGGER.error("Neustart fehlgeschlagen.")

    hass.services.async_register(
        DOMAIN,
        "set_battery_power",
        handle_set_battery_power,
        schema=vol.Schema({
            vol.Required("direction"): vol.In(["charge", "discharge"]),
            vol.Required("watts"): vol.All(vol.Coerce(int), vol.Range(min=0)),
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "set_em_operating_mode",
        handle_set_em_operating_mode,
        schema=vol.Schema({
            vol.Required("mode"): vol.All(vol.Coerce(int), vol.Range(min=1, max=11)),
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "get_system_status",
        handle_get_system_status,
        schema=vol.Schema({
            vol.Optional("include_raw", default=False): cv.boolean,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "restart_battery",
        handle_restart_battery,
        schema=vol.Schema({
            vol.Required("confirm"): cv.boolean,
        }),
    )

    _LOGGER.info("Alle Services für Sonnen-Batterie erfolgreich registriert.")
