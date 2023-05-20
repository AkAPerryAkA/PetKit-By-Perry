# MODULE IMPORT #
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType, aiohttp_client
import voluptuous as vol
import tzlocal
import locale
import pytz
from pytz import country_timezones
# VARIABLE/DEFINITION IMPORT #
from .Core import getCountryCode, sendRequest
from .const import DOMAIN, API_REGION_SERVERS, API_SERVERS

class PetKitByPerryConfigFlow(config_entries.ConfigFlow, domain = DOMAIN):
    def __init__(self, hass: HomeAssistant, config: dict):
        self.http = aiohttp_client.async_create_clientsession(hass, auto_cleanup=False)

    async def async_step_user(self, user_input=None):
        # Specify items in the order they are to be displayed in the UI
        errors = {}
        if user_input is not None:
            # Validate user input
            valid = await is_valid(user_input)
            if valid:
                # See next section on create entry usage
                return self.async_create_entry(...)

            errors["base"] = "auth_error"
        
        API_SERVERS.clear()
        for CountryCode in (await self.http.request('GET', API_REGION_SERVERS)):
            API_SERVERS.append([list(CountryCode.values())[2], list(CountryCode.values())[1]])
        
        STEP_USER_DATA_SCHEMA = vol.Schema(
            {
                vol.Required('Username'): TextSelector(TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="username")),
                vol.Required('Password'): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")),
                vol.Optional("Country Code", default=getCountryCode(str(tzlocal.get_localzone()))): vol.In(list(dict(country_timezones.items()).keys())),
                vol.Optional("Timezone", default=str(tzlocal.get_localzone())): vol.In(list(dict(API_SERVERS).keys())),
            }
        )

        return self.async_show_form(step_id="init", data_schema=STEP_USER_DATA_SCHEMA)