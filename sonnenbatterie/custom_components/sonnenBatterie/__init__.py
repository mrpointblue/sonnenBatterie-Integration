from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
import logging

from .const import DOMAIN
from .service import async_register_services

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the sonnenbatterie integration for sensor readings and services."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    try:
        # Forward setup for sensor platform
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

        # Register services
        ip = entry.data.get("ip_address")
        token = entry.data.get("token")
        await async_register_services(hass, entry.data, ip, token)

        _LOGGER.info("Sonnenbatterie integration successfully set up.")
        return True
    except ConfigEntryNotReady as e:
        _LOGGER.error(f"Config entry not ready: {e}")
        raise
    except Exception as e:
        _LOGGER.error(f"Failed to set up sonnenbatterie integration: {e}")
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
        if unload_ok and entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)
        return unload_ok
    except Exception as e:
        _LOGGER.error(f"Failed to unload entry for sonnenbatterie: {e}")
        return False


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """
    Update an existing configuration entry.

    This is called when options or entry data are updated via the OptionsFlow.
    """
    _LOGGER.info(f"Updating configuration for entry: {entry.entry_id}")
    try:
        # Reload the entry to apply changes
        await async_unload_entry(hass, entry)
        await async_setup_entry(hass, entry)
        _LOGGER.info(f"Successfully updated configuration for entry: {entry.entry_id}")
    except Exception as e:
        _LOGGER.error(f"Failed to update configuration for sonnenbatterie entry: {e}")