# MODULE IMPORT #
from homeassistant import config_entries
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType
import voluptuous as vol
import tzlocal
from babel import Locale
import logging
from typing import Any, Dict, Optional
# VARIABLE/DEFINITION IMPORT #
from .Core import getCountryCode, getAPIServers, getAPIToken
from .const import DOMAIN, API_COUNTRY, API_TIMEZONE

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class PetKitByPerryConfigFlow(config_entries.ConfigFlow, domain = DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                valid = await getAPIToken(user_input['username'], user_input['password'], user_input['country'], user_input['timezone'])
            except ValueError:
                errors["base"] = "auth"
            if errors is {}:
                await self.async_set_unique_id(valid["UserID"])
                self._abort_if_unique_id_configured()
                _LOGGER.info('New account added with the username {}'.format(user_input['username']))
                return self.async_create_entry(title="Account_{}".format(valid["UserID"]), data=valid)
        await getAPIServers()
        STEP_USER_DATA_SCHEMA = vol.Schema(
            {
                vol.Required("username"): TextSelector(TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="username")),
                vol.Required("password"): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")),
                vol.Required("country", default=dict(API_COUNTRY).get(str(Locale(getCountryCode(str(tzlocal.get_localzone())).replace('_', '-').upper())))): vol.In(sorted(list(dict(API_COUNTRY).values()))),
                vol.Required("timezone", default=dict(API_TIMEZONE).get(str(Locale(getCountryCode(str(tzlocal.get_localzone())).replace('_', '-').upper())))): vol.In(sorted(list(dict(API_TIMEZONE).values()))),
            }
        )
        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)