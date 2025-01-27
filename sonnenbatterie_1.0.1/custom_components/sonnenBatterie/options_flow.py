from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from .const import DEFAULT_PREFIX

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
                    "custom_prefix": user_input.get("custom_prefix", DEFAULT_PREFIX),
                    "charge_discharge_direction": user_input["charge_discharge_direction"],
                    "charge_discharge_power": user_input["charge_discharge_power"],
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
                vol.Optional(
                    "custom_prefix", default=self.config_entry.data.get("custom_prefix", DEFAULT_PREFIX)
                ): cv.string,
                vol.Required(
                    "charge_discharge_direction",
                    default=self.config_entry.data.get("charge_discharge_direction", "charge"),
                ): vol.In(["charge", "discharge"]),  # Auswahl: Laden oder Entladen
                vol.Required(
                    "charge_discharge_power",
                    default=self.config_entry.data.get("charge_discharge_power", 1000),
                ): vol.All(vol.Coerce(int), vol.Range(min=0)),  # Leistung in Watt
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)