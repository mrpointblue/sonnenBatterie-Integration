from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

class SonnenOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for the SonnenBatterie integration."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    "ip_address": user_input["ip_address"],
                    "token": user_input["token"],
                    "scan_interval": user_input["scan_interval"],
                },
            )
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required("ip_address", default=self.config_entry.data["ip_address"]): cv.string,
                vol.Required("token", default=self.config_entry.data["token"]): cv.string,
                vol.Required(
                    "scan_interval", default=self.config_entry.data.get("scan_interval", 30)
                ): vol.All(vol.Coerce(int), vol.Range(min=5)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
