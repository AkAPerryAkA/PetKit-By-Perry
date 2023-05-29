# MODULE IMPORT #
from homeassistant.core import HomeAssistant, callback
from homeassistant import config_entries, exceptions
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType
import voluptuous as vol
import tzlocal
from babel import Locale
import logging
from typing import Any, Dict, Optional
from asyncio import TimeoutError
from aiohttp import ClientConnectorError, ContentTypeError
# VARIABLE/DEFINITION IMPORT #
from .Core import getCountryCode, getAPIServers, getAPIToken, CannotConnect
from .const import DOMAIN, API_COUNTRY, API_TIMEZONE

_LOGGER = logging.getLogger(__name__)

@callback
def petkit_config_entries(hass: HomeAssistant):
    """Return the hosts already configured."""
    return set(entry.data['Username'] for entry in hass.config_entries.async_entries(DOMAIN))

class ConfigFlow(config_entries.ConfigFlow, domain = DOMAIN):
    def account_in_configuration_exists(self, account) -> bool:
        """Return True if host exists in configuration."""
        if account in petkit_config_entries(self.hass):
            return True
        return False

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                if self.account_in_configuration_exists(user_input['username'].lower()):
                    return self.async_abort(reason="already_configured")
                await self.async_set_unique_id(user_input['username'].lower())
                self._abort_if_unique_id_configured()
                _LOGGER.debug("Authenticating %s", user_input['username'])
                valid = await getAPIToken(user_input['username'], user_input['password'], user_input['country'], user_input['timezone'])
                _LOGGER.debug("New account added with the username %s", user_input['username'])
                return self.async_create_entry(title=valid["Username"], data=valid)
            except CannotConnect:
                errors["base"] = "auth"
            except ValueError as error:
                errors["base"] = "err"
                _LOGGER.debug('Login failed: %s', error)
        await getAPIServers()
        STEP_USER_DATA_SCHEMA = vol.Schema(
            {
                vol.Required("username"): TextSelector(TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="username")),
                vol.Required("password"): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")),
                vol.Required("country", default=dict(API_COUNTRY).get(str(Locale(getCountryCode(str(tzlocal.get_localzone())).replace('_', '-').upper())))): vol.In(sorted(list(dict(API_COUNTRY).values()))),
                vol.Required("timezone", default=dict(API_TIMEZONE).get(str(Locale(getCountryCode(str(tzlocal.get_localzone())).replace('_', '-').upper())))): vol.In(sorted(list(dict(API_TIMEZONE).values()))),
            }
        )
        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)