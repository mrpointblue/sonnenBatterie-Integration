from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, DEFAULT_PREFIX


class SonnenBatterieConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SonnenBatterie integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="SonnenBatterie",
                data={
                    "ip_address": user_input["ip_address"],
                    "token": user_input["token"],
                    "scan_interval": user_input["scan_interval"],
                    "custom_prefix": user_input.get("custom_prefix", DEFAULT_PREFIX),
                },
            )

        schema = vol.Schema(
            {
                vol.Required("ip_address"): cv.string,
                vol.Required("token"): cv.string,
                vol.Required("scan_interval", default=30): vol.All(vol.Coerce(int), vol.Range(min=5)),
                vol.Optional("custom_prefix", default=DEFAULT_PREFIX): cv.string,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return SonnenOptionsFlow(config_entry)


class SonnenOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for SonnenBatterie integration."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
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
            return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required("ip_address", default=self.entry.data["ip_address"]): cv.string,
                vol.Required("token", default=self.entry.data["token"]): cv.string,
                vol.Required("scan_interval", default=self.entry.data.get("scan_interval", 30)): vol.All(vol.Coerce(int), vol.Range(min=5)),
                vol.Optional("custom_prefix", default=self.entry.data.get("custom_prefix", DEFAULT_PREFIX)): cv.string,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)