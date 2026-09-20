"""Write commands using Home Assistant's shared HTTP session."""
import asyncio
import aiohttp
from homeassistant.exceptions import HomeAssistantError

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
    if mode not in (1, 2, 6, 10):
        raise HomeAssistantError("Unsupported operating mode")
    await _request(session, "PUT", ip, token, "configurations", {"EM_OperatingMode": str(mode)})

async def set_battery_power(session, ip, token, direction, watts):
    if direction not in ("charge", "discharge") or watts < 0:
        raise HomeAssistantError("Invalid power setpoint")
    await _request(session, "POST", ip, token, f"setpoint/{direction}/{watts}")
