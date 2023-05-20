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
    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_auth(user_input[CONF_ACCESS_TOKEN], self.hass)
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                # Input is valid, set data.
                self.data = user_input
                self.data[CONF_REPOS] = []
                # Return the form of the next step.
                return await self.async_step_repo()
        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )