from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN
from .const import DEFAULT_PREFIX

class SonnenBatterieConfigFlow(config_entries.ConfigFlow, domain="sonnenBatterie"):
    """Handle a config flow for SonnenBatterie."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            ip = user_input.get("ip_address")
            token = user_input.get("token")
            scan_interval = user_input.get("scan_interval")
            custom_prefix = user_input.get("custom_prefix", DEFAULT_PREFIX)

            if not ip or not token:
                errors["base"] = "invalid_credentials"
            elif scan_interval < 5:
                errors["scan_interval"] = "too_short"
            else:
                return self.async_create_entry(
                    title="SonnenBatterie",
                    data={
                        "ip_address": ip,
                        "token": token,
                        "scan_interval": scan_interval,
                        "custom_prefix": custom_prefix,
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
        from .options_flow import SonnenOptionsFlow
        return SonnenOptionsFlow(config_entry)
