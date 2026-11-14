"""Write commands using Home Assistant's shared HTTP session."""
import asyncio
import aiohttp
from homeassistant.exceptions import HomeAssistantError
from .const import SITE_LIMIT_KEYS

async def _request(session, method, ip, token, path, data=None):
    try:
        async with session.request(
            method, f"http://{ip}/api/v2/{path}", headers={"Auth-Token": token},
            data=data, timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            response.raise_for_status()
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        raise HomeAssistantError("sonnenBatterie command failed") from err

async def set_em_operating_mode(session, ip, token, mode):
    if mode not in (1, 2, 6, 10, 11):
        raise HomeAssistantError("Unsupported operating mode")
    await _request(session, "PUT", ip, token, "configurations", {"EM_OperatingMode": str(mode)})

async def set_battery_power(session, ip, token, direction, watts):
    if direction not in ("charge", "discharge") or watts < 0:
        raise HomeAssistantError("Invalid power setpoint")
    await _request(session, "POST", ip, token, f"setpoint/{direction}/{watts}")


async def _check_site_endpoint(session, ip, token, endpoint):
    """Check the selected device without issuing a write or trying legacy fallback."""
    try:
        async with session.request(
            "GET", f"http://{ip}/api/v2/{endpoint}",
            headers={"Auth-Token": token}, timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            response.raise_for_status()
            payload = await response.json()
            keys = SITE_LIMIT_KEYS if endpoint == "site/limits" else ("p_bess_inv_export_import_setpoint",)
            if not isinstance(payload, dict) or not any(key in payload for key in keys):
                raise HomeAssistantError("Site API is not supported by this battery")
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
        raise HomeAssistantError("Site API unavailable or not supported by this battery") from err


def _duration(seconds):
    if type(seconds) is not int or not 1 <= seconds <= 86400:
        raise HomeAssistantError("Duration must be 1–86400 whole seconds")
    return f"PT{seconds}S"


async def set_site_setpoint(session, ip, token, watts, duration=30):
    """Positive = AC import, negative = AC export; zero is an active command."""
    if type(watts) is not int or not -2147483648 <= watts <= 2147483647:
        raise HomeAssistantError("Setpoint must be an int32 watt value")
    data = {"p_bess_inv_export_import_setpoint": watts, "duration": _duration(duration)}
    await _check_site_endpoint(session, ip, token, "site/setpoint")
    await _request(session, "PUT", ip, token, "site/setpoint", data)


async def set_site_limits(session, ip, token, limits, duration=30):
    if not limits or any(key not in SITE_LIMIT_KEYS or type(value) is not int
                         or not 0 <= value <= 2147483647 for key, value in limits.items()):
        raise HomeAssistantError("Specify at least one non-negative int32 site limit")
    data = {**limits, "duration": _duration(duration)}
    await _check_site_endpoint(session, ip, token, "site/limits")
    await _request(session, "PUT", ip, token, "site/limits", data)
