"""Register services once and resolve the battery for every call."""
import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv, entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .battery_control import set_battery_power, set_em_operating_mode

SERVICES = ("set_battery_power", "set_em_operating_mode", "publish_all_sensors")


def resolve_entry(hass, entity_ids):
    entries = hass.data.get(DOMAIN, {})
    if not entity_ids:
        if len(entries) != 1:
            raise HomeAssistantError("Select an entity of exactly one loaded sonnenBatterie")
        return next(iter(entries.values()))
    registry = er.async_get(hass)
    selected = set()
    for entity_id in entity_ids:
        entity = registry.async_get(entity_id)
        if entity is None or entity.platform != DOMAIN or entity.config_entry_id not in entries:
            raise HomeAssistantError("Target is not a loaded sonnenBatterie entity")
        selected.add(entity.config_entry_id)
    if len(selected) != 1:
        raise HomeAssistantError("Select entities belonging to exactly one battery")
    return entries[selected.pop()]


async def async_register_services(hass):
    if hass.services.has_service(DOMAIN, "set_battery_power"):
        return

    async def handle_control(call):
        entry = resolve_entry(hass, call.data.get("entity_id"))
        config = {**entry.data, **entry.options}
        session = async_get_clientsession(hass)
        args = (session, config["ip_address"], config["token"])
        if call.service == "set_battery_power":
            await set_battery_power(*args, call.data["direction"], call.data["watts"])
        else:
            await set_em_operating_mode(*args, call.data["mode"])

    target = {vol.Optional("entity_id"): cv.entity_ids}
    hass.services.async_register(DOMAIN, "set_battery_power", handle_control, schema=vol.Schema({
        **target,
        vol.Required("direction"): vol.In(["charge", "discharge"]),
        vol.Required("watts"): vol.All(vol.Coerce(int), vol.Range(min=0)),
    }))
    hass.services.async_register(DOMAIN, "set_em_operating_mode", handle_control, schema=vol.Schema({
        **target, vol.Required("mode"): vol.All(vol.Coerce(int), vol.In([1, 2, 6, 10])),
    }))

    async def publish(call):
        registry = er.async_get(hass)
        for state in hass.states.async_all():
            entity = registry.async_get(state.entity_id)
            if entity and entity.platform == DOMAIN and entity.config_entry_id in hass.data.get(DOMAIN, {}):
                hass.bus.async_fire("sonnenbatterie_sensor_published", {
                    "entity_id": state.entity_id, "state": state.state,
                })

    hass.services.async_register(DOMAIN, "publish_all_sensors", publish)


def async_remove_services(hass):
    for service in SERVICES:
        hass.services.async_remove(DOMAIN, service)
