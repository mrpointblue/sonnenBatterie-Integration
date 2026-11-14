"""Shared polling coordinator, initialized before sensor platform setup."""
import asyncio
from datetime import timedelta
import logging

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SENSORS, DEFAULT_SCAN_INTERVAL, MIN_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

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
                    # HTTP errors affect this endpoint only. Keep the configured
                    # token and let normal polling retry; never start reauthentication.
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

