from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, DEFAULT_PREFIX

DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 5


class SonnenBatterieConfigFlow(
    config_entries.ConfigFlow, config_entries.OptionsFlowWithConfigEntry
):
    """Combined Config and Options Flow for SonnenBatterie."""

    VERSION = 1

    def __init__(self):
        self.entry = None

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="SonnenBatterie", data=user_input)

        schema = vol.Schema(
            {
                vol.Required("ip_address"): cv.string,
                vol.Required("token"): cv.string,
                vol.Optional(
                    "scan_interval", default=DEFAULT_SCAN_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
                vol.Optional("custom_prefix", default=DEFAULT_PREFIX): cv.string,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_init(self, user_input=None):
        """Options flow."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.entry,
                data={
                    "ip_address": user_input["ip_address"],
                    "token": user_input["token"],
                    "scan_interval": user_input["scan_interval"],
                    "custom_prefix": user_input.get("custom_prefix", DEFAULT_PREFIX),
                },
            )
            await self.hass.config_entries.async_reload(self.entry.entry_id)
            return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required(
                    "ip_address", default=self.entry.data["ip_address"]
                ): cv.string,
                vol.Required("token", default=self.entry.data["token"]): cv.string,
                vol.Required(
                    "scan_interval",
                    default=self.entry.data.get(
                        "scan_interval", DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
                vol.Optional(
                    "custom_prefix",
                    default=self.entry.data.get("custom_prefix", DEFAULT_PREFIX),
                ): cv.string,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        from .options_flow import SonnenOptionsFlow

        return SonnenOptionsFlow(config_entry)
