"""Set up the sonnenBatterie integration."""
import logging
from pathlib import Path
import shutil

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, PLATFORMS, DEFAULT_PREFIX
from .service import async_register_services, async_remove_services

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
_LOGGER = logging.getLogger(__name__)
CARD_FILE_NAME = "sonnenbatteriecard.js"

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Freeze the legacy identity once, preserving existing registry entries even
    # after the user changes the connection address or the display prefix.
    data = dict(entry.data)
    data.setdefault("identity_ip", data["ip_address"])
    data.setdefault("identity_prefix", data.get("custom_prefix", DEFAULT_PREFIX))
    if data != entry.data:
        hass.config_entries.async_update_entry(entry, data=data)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry
    await async_register_services(hass)
    entry.async_on_unload(entry.add_update_listener(async_update_entry))
    await copy_card_to_www(hass)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    hass.data[DOMAIN].pop(entry.entry_id, None)
    if not hass.data[DOMAIN]:
        async_remove_services(hass)
    return True

async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)

async def copy_card_to_www(hass: HomeAssistant) -> None:
    """Copy in the executor; resource registration is managed by the user."""
    def copy():
        source = Path(__file__).parent / "card_resources" / CARD_FILE_NAME
        target = Path(hass.config.path("www", CARD_FILE_NAME))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    try:
        await hass.async_add_executor_job(copy)
    except OSError:
        _LOGGER.exception("Could not copy the optional dashboard card")
