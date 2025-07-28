# File: custom_components/sonnenbatterie/config_flow.py

from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, DEFAULT_PREFIX

DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 5

class SonnenBatterieConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for the SonnenBatterie integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
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

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        from .options_flow import SonnenOptionsFlow
        return SonnenOptionsFlow(config_entry)