# MODULE IMPORT #
from homeassistant import config_entries
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType
import voluptuous as vol
import tzlocal
import locale
from pytz import country_timezones
from babel import Locale
# VARIABLE/DEFINITION IMPORT #
from .Core import getCountryCode, getAPIServers
from .const import DOMAIN, API_COUNTRY, API_TIMEZONE

@config_entries.HANDLERS.register(DOMAIN)
class PetKitByPerryConfigFlow(config_entries.ConfigFlow, domain = DOMAIN):
    async def async_step_user(self, user_input=None):
        # Specify items in the order they are to be displayed in the UI
        errors = {}
        if user_input is not None:
            # Validate user input
            #valid = await is_valid(user_input)
            
            if valid:
                # See next section on create entry usage
                return self.async_create_entry(...)

            errors["base"] = "auth_error"
        await getAPIServers()
        STEP_USER_DATA_SCHEMA = vol.Schema(
            {
                vol.Required('Username'): TextSelector(TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="username")),
                vol.Required('Password'): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")),
                vol.Required("Country", default=dict(API_COUNTRY).get(str(Locale(getCountryCode(str(tzlocal.get_localzone())).replace('_', '-').upper())))): vol.In(sorted(list(dict(API_COUNTRY).values()))),
                vol.Required("Timezone", default=dict(API_TIMEZONE).get(str(Locale(getCountryCode(str(tzlocal.get_localzone())).replace('_', '-').upper())))): vol.In(sorted(list(dict(API_TIMEZONE).values()))),
            }
        )

        return self.async_show_form(step_id="init", data_schema=STEP_USER_DATA_SCHEMA)