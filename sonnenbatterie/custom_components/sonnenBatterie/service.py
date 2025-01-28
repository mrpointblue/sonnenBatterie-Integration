import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .battery_control import set_em_operating_mode, set_battery_power

_LOGGER = logging.getLogger(__name__)
_LOGGER.debug("Service set_battery_power registered")
_LOGGER.debug("Service set_em_operating_mode registered")

DOMAIN = "sonnenbatterie"

async def async_register_services(hass: HomeAssistant, config: dict, ip: str, token: str):
    """
    Registriert die Lade-/Entlade- und EM_OperatingMode-Services in Home Assistant.
    """
    async def handle_set_battery_power(call: ServiceCall):
        """
        Service-Handler für das Setzen der Lade-/Entladeleistung.
        """
        direction = call.data.get("direction")
        watts = call.data.get("watts", 1000)  # Standardwert: 1000 Watt
        mode = call.data.get("mode", 2)  # Standard-Mode ist 2, falls kein Wert angegeben wird

        # Validierung der Eingabe
        if direction not in ["charge", "discharge"]:
            _LOGGER.error(f"Ungültige Richtung: {direction}. Muss 'charge' oder 'discharge' sein.")
            return

        if watts < 0:
            _LOGGER.error(f"Ungültiger Watt-Wert: {watts}. Muss größer oder gleich 0 sein.")
            return

        # 1. EM_OperatingMode setzen
        _LOGGER.debug(f"Setze EM_OperatingMode auf: {mode}.")
        success = await set_em_operating_mode(ip, token, mode=mode)
        if not success:
            _LOGGER.error(f"EM_OperatingMode konnte nicht auf {mode} gesetzt werden.")
            return

        # 2. Batterie laden oder entladen
        _LOGGER.debug(f"Setze Batterieleistung: direction={direction}, watts={watts}")
        success = await set_battery_power(ip, token, direction, watts)
        if not success:
            _LOGGER.error(f"Fehler beim Setzen der Batterieleistung: {direction}, {watts}W")
        else:
            _LOGGER.info(f"Batterieleistung erfolgreich gesetzt: {direction}, {watts}W")

    async def handle_set_em_operating_mode(call: ServiceCall):
        """
        Service-Handler für das Setzen des EM_OperatingMode.
        """
        mode = call.data.get("mode", 2)  # Standard-Mode ist 2

        # EM_OperatingMode setzen
        _LOGGER.debug(f"Setze EM_OperatingMode auf: {mode}")
        success = await set_em_operating_mode(ip, token, mode)
        if not success:
            _LOGGER.error(f"EM_OperatingMode konnte nicht auf {mode} gesetzt werden.")
        else:
            _LOGGER.info(f"EM_OperatingMode erfolgreich auf {mode} gesetzt.")

    # Service für Batterieleistung registrieren
    hass.services.async_register(
        DOMAIN,
        "set_battery_power",
        handle_set_battery_power,
        schema=vol.Schema({
            vol.Required("direction"): vol.In(["charge", "discharge"]),  # Nur 'charge' oder 'discharge' erlaubt
            vol.Required("watts"): vol.All(vol.Coerce(int), vol.Range(min=0)),  # Leistung ≥ 0
            vol.Optional("mode"): vol.All(vol.Coerce(int), vol.Range(min=1, max=11)),  # Optionaler Mode (1-11)
        }),
    )

    # Service für EM_OperatingMode registrieren
    hass.services.async_register(
        DOMAIN,
        "set_em_operating_mode",
        handle_set_em_operating_mode,
        schema=vol.Schema({
            vol.Required("entry_id"): cv.string,
            vol.Required("mode"): vol.All(vol.Coerce(int), vol.Range(min=1, max=11)),  # Wertebereich: 1-11
        }),
    )

    _LOGGER.info("Services für Sonnen-Batterie erfolgreich registriert.")
