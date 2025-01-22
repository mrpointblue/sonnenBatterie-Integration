from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the sonnenBatterie integration for sensor readings."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    try:
        # Forward setup for sensor platform
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        return True
    except ConfigEntryNotReady as e:
        _LOGGER.error(f"Config entry not ready: {e}")
        raise
    except Exception as e:
        _LOGGER.error(f"Failed to forward setup for sonnenBatterie sensors: {e}")
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
        if unload_ok and entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)
        return unload_ok
    except Exception as e:
        _LOGGER.error(f"Failed to unload entry for sonnenBatterie: {e}")
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
        _LOGGER.error(f"Failed to update configuration for sonnenBatterie entry: {e}")
