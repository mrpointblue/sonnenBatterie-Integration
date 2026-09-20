"""Configure sonnenBatterie."""
import asyncio
import aiohttp
import voluptuous as vol
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv
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

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        entry = self._get_reauth_entry()
        errors = {}
        if user_input is not None:
            config = {**entry.data, **entry.options, **user_input}
            try:
                async with async_get_clientsession(self.hass).get(
                    f"http://{config['ip_address']}/api/v2/status",
                    headers={"Auth-Token": config["token"]},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status in (401, 403):
                        errors["base"] = "invalid_auth"
                    else:
                        response.raise_for_status()
            except (aiohttp.ClientError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
            if not errors:
                self.hass.config_entries.async_update_entry(
                    entry, options={**entry.options, **user_input})
                # Loaded entries reload through their update listener; failed
                # initial setups have no listener and need an explicit reload.
                if not entry.update_listeners:
                    self.hass.config_entries.async_schedule_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")
        return self.async_show_form(
            step_id="reauth_confirm", errors=errors,
            data_schema=vol.Schema({vol.Required("token"): cv.string}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SonnenOptionsFlow()
