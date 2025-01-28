import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "http://{ip}/api/v2"

async def set_em_operating_mode(ip: str, token: str, mode: int) -> bool:
    """
    Setzt den EM_OperatingMode auf den angegebenen Wert.

    :param ip: IP-Adresse des Geräts.
    :param token: Authentifizierungstoken.
    :param mode: Modus (z. B. 1 für manuell, 2 für Eigenverbrauchsoptimierung).
    :return: True, wenn erfolgreich, sonst False.
    """
    url = f"{API_BASE_URL.format(ip=ip)}/configurations"
    headers = {
        "Auth-Token": token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    # URL-encoded payload
    payload = {"EM_OperatingMode": str(mode)}

    _LOGGER.debug(f"Sende PUT-Anfrage an {url} mit payload: {payload}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.put(url, data=payload, headers=headers) as response:
                if response.status == 200:
                    _LOGGER.info(f"EM_OperatingMode erfolgreich auf {mode} gesetzt.")
                    return True
                else:
                    error_message = await response.text()
                    _LOGGER.error(
                        f"Fehler beim Setzen des EM_OperatingMode: {response.status}, Antwort: {error_message}"
                    )
                    return False
        except Exception as e:
            _LOGGER.error(f"Exception beim Setzen des EM_OperatingMode: {e}")
            return False


async def set_battery_power(ip: str, token: str, direction: str, watts: int) -> bool:
    """
    Setzt die Lade- oder Entladeleistung der Batterie.

    :param ip: IP-Adresse des Geräts.
    :param token: Authentifizierungstoken.
    :param direction: Richtung der Leistung ("charge" oder "discharge").
    :param watts: Leistung in Watt (≥ 0).
    :return: True, wenn erfolgreich, sonst False.
    """
    # Eingabevalidierung
    if direction not in ["charge", "discharge"]:
        _LOGGER.error("Ungültige Richtung. Verwenden Sie 'charge' oder 'discharge'.")
        return False

    if watts <= 0:
        _LOGGER.error("Watt-Leistung muss größer als 0 sein.")
        return False

    url = f"{API_BASE_URL.format(ip=ip)}/setpoint/{direction}/{watts}"
    headers = {
        "Auth-Token": token,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    _LOGGER.debug(f"Sende POST-Anfrage an {url} mit direction={direction} und watts={watts}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers) as response:
                if response.status == 200:
                    _LOGGER.info(f"Batterieleistung erfolgreich gesetzt: {direction}, {watts}W")
                    return True
                else:
                    error_message = await response.text()
                    _LOGGER.error(
                        f"Fehler beim Setzen der Batterieleistung: {response.status}, Antwort: {error_message}"
                    )
                    return False
        except Exception as e:
            _LOGGER.error(f"Exception beim Setzen der Batterieleistung: {e}")
            return False