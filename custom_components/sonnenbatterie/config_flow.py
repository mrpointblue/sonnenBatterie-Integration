"""Configure sonnenBatterie."""
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .options_flow import SonnenOptionsFlow, config_schema


class SonnenBatterieConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Prevent configuring the same host twice. Authentication is checked
            # by the first coordinator refresh during setup.
            host = user_input["ip_address"].strip().lower()
            for entry in self._async_current_entries():
                current = {**entry.data, **entry.options}
                if current["ip_address"].strip().lower() == host:
                    return self.async_abort(reason="already_configured")
            return self.async_create_entry(title="SonnenBatterie", data=user_input)
        return self.async_show_form(step_id="user", data_schema=config_schema())

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SonnenOptionsFlow()
