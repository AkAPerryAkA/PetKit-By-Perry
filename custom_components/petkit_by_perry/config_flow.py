from homeassistant import config_entries, core
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME, CONF_PATH, CONF_URL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get,
)
import voluptuous as vol
from .const import DOMAIN

AUTH_SCHEMA = vol.Schema(
    {vol.Required(CONF_ACCESS_TOKEN): cv.string, vol.Optional(CONF_URL): cv.string}
)

class PetKitConfigFlow(config_entries.ConfigFlow, domain = DOMAIN):
    async def async_step_user(self, user_input = None):
        """Invoked when a user initiates a flow via the user interface."""
        if user_input is not None:
            return True
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required("password"): str})
        )