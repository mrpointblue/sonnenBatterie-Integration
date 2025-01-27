import os
import shutil
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .service import async_register_services

_LOGGER = logging.getLogger(__name__)
_LOGGER.info("Die sonnenbatterie-Integration wird geladen...")

CARD_FILE_NAME = "sonnenbatterie-card.js"
CARD_SOURCE_FOLDER = "custom_components/sonnenbatterie/card_resources"
CARD_TARGET_FOLDER = "www"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the sonnenbatterie integration for sensor readings and services."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    try:
        # Forward setup for sensor platform
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

        # Kopiere die Karte in den www-Ordner
        if not await copy_card_to_www(hass):
            _LOGGER.warning("Die Karte konnte nicht in den www-Ordner kopiert werden.")

        # Registriere die Karte als Lovelace-Ressource
        await add_lovelace_resource(hass, f"/local/{CARD_FILE_NAME}")

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


async def copy_card_to_www(hass: HomeAssistant) -> bool:
    """
    Kopiert die benutzerdefinierte Karte in den www-Ordner.
    """
    try:
        source_path = os.path.join(hass.config.path(), CARD_SOURCE_FOLDER, CARD_FILE_NAME)
        target_path = os.path.join(hass.config.path(), CARD_TARGET_FOLDER, CARD_FILE_NAME)

        # Sicherstellen, dass der www-Ordner existiert
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        # Karte kopieren
        shutil.copyfile(source_path, target_path)
        _LOGGER.info(f"Karte erfolgreich kopiert: {target_path}")
        return True
    except Exception as e:
        _LOGGER.error(f"Fehler beim Kopieren der Karte: {e}")
        return False


async def add_lovelace_resource(hass: HomeAssistant, resource_url: str) -> None:
    """
    Fügt die benutzerdefinierte Karte als Lovelace-Ressource hinzu.
    """
    try:
        # Zugriff auf die Lovelace-Ressourcen
        resources = hass.data.get("lovelace", {}).get("resources", None)

        if resources is not None:
            # Prüfen, ob die Ressource bereits existiert
            existing_resources = [res.get("url") for res in resources.async_items()]
            if resource_url in existing_resources:
                _LOGGER.info(f"Ressource {resource_url} ist bereits registriert.")
                return

            # Ressource hinzufügen
            await resources.async_create_item({"res_type": "module", "url": resource_url})
            _LOGGER.info(f"Ressource {resource_url} erfolgreich registriert.")
        else:
            _LOGGER.warning("Lovelace-Ressourcen konnten nicht gefunden werden.")
    except Exception as e:
        _LOGGER.error(f"Fehler beim Hinzufügen der Ressource: {e}")