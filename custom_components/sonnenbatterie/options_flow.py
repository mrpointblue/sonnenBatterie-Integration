"""Options for sonnenBatterie."""
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from .const import DEFAULT_PREFIX, DEFAULT_SCAN_INTERVAL, MIN_SCAN_INTERVAL


def config_schema(data=None):
    data = data or {}
    return vol.Schema({
        vol.Required("ip_address", default=data.get("ip_address", "")): cv.string,
        vol.Required("token", default=data.get("token", "")): cv.string,
        vol.Required("scan_interval", default=data.get("scan_interval", DEFAULT_SCAN_INTERVAL)):
            vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
        vol.Optional("custom_prefix", default=data.get("custom_prefix", DEFAULT_PREFIX)): cv.string,
    })


class SonnenOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        data = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=config_schema(data))
