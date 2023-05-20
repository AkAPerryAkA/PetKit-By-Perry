from homeassistant import config_entries, core
import voluptuous as vol
from .const import DOMAIN
from homeassistant.helpers.selector import selector

class PetKitByPerryConfigFlow(config_entries.ConfigFlow, domain = DOMAIN):
    async def async_step_user(self, user_input=None):
        # Specify items in the order they are to be displayed in the UI
        
        STEP_USER_DATA_SCHEMA = vol.Schema(
            {
                vol.Required('Username'): TextSelector(TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="username")),
                vol.Required('Password'): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")),
                vol.Required("Country"): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="country")),
                vol.Required("TimeZone"): TextSelector(TextSelectorConfig(type=TextSelectorType.TEL, autocomplete="timezone")),
            }
        )

        return self.async_show_form(step_id="init", data_schema=STEP_USER_DATA_SCHEMA)