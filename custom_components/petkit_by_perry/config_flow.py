# MODULE IMPORT #
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType
from homeassistant.core import HomeAssistant, callback
from homeassistant import config_entries, exceptions
from datetime import datetime, timedelta
from pytz import country_timezones
from babel import Locale
import voluptuous as vol
import datetime
import aiohttp
import tzlocal
import hashlib
import tzlocal
import logging
import locale
import pytz
import re
# VARIABLE/DEFINITION IMPORT #
from .const import DOMAIN, API_COUNTRY, API_TIMEZONE, API_SERVERS, API_LOGIN_PATH, API_REGION_SERVERS
_LOGGER = logging.getLogger(__name__)

@callback
def petkit_config_entries(hass: HomeAssistant):
    return set(entry.data['Username'] for entry in hass.config_entries.async_entries(DOMAIN))

def get_country_code(TimeZone):
    for countrycode in country_timezones:
        for timezone in country_timezones[countrycode]:
            if timezone == TimeZone:
                return countrycode.upper()
    return next(iter(country_timezones))

class ConfigFlow(config_entries.ConfigFlow, domain = DOMAIN):
    def account_in_configuration_exists(self, account) -> bool:
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

                if re.findall(r"([a-fA-F\d]{32})", user_input['password']):
                    user_input['password'] = user_input['password'].lower()
                else:
                    _LOGGER.debug('config_flow: Password is not MD5 :O')
                    hash = hashlib.md5()
                    hash.update(user_input['password'].encode("utf-8"))
                    user_input['password'] = hash.hexdigest()
                header = {
                    "User-Agent": "PETKIT/7.26.1 (iPhone; iOS 14.7.1; Scale/3.00)",
                    "X-Timezone": f"{round(pytz.timezone(user_input['timezone'])._utcoffset.seconds/60/60)}.0",
                    "X-Api-Version": "7.26.1",
                    "X-Img-Version": "1",
                    "X-TimezoneId": pytz.timezone(user_input['timezone']).zone,
                    "X-Client": "ios(14.7.1;iPhone13,4)",
                    "X-Locale": locale.getdefaultlocale()[0].replace("-", "_"),
                }
                param = {
                    "timezoneId": pytz.timezone(user_input['timezone']).zone,
                    "timezone": f"{round(pytz.timezone(user_input['timezone'])._utcoffset.seconds/60/60)}.0",
                    "username": user_input['username'],
                    "password": user_input['password'],
                    "locale": locale.getdefaultlocale()[0],
                    "encrypt": 1,
                }
                async with aiohttp.ClientSession(headers=header) as session:
                    async with session.post(url=(dict(API_SERVERS).get(list(dict(API_COUNTRY).keys())[list(dict(API_COUNTRY).values()).index(user_input['country'])]) + API_LOGIN_PATH), params=param) as response:
                        result = await response.json()
                if list(result.keys())[0] == 'result':
                    _LOGGER.debug('config_flow: Authentication returned result')
                    if list(result['result'])[0] == 'list':
                        result = result['result']['list']
                    else:
                        result = result['result']
                elif list(result.keys())[0] == 'error':
                    _LOGGER.debug('config_flow: Authentication returned error: %s', result['error']['msg'])
                    raise CannotConnect(result['error']['msg'])
                else:
                    _LOGGER.debug('config_flow: Authentication returned unknown value')
                    raise Exception('Unknown API response')
                account = {
                    "UserID": result['user']['account']['userId'],
                    "Username": user_input['username'],
                    "Password": user_input['password'],
                    "Country": user_input['country'],
                    "TimeZone": str(pytz.timezone(user_input['timezone'])),
                    "Token": result['session']['id'],
                    "Token_Created": str(datetime.strptime(result['session']["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")),
                    "Token_Expires": str(datetime.strptime(result['session']["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(seconds = result['session']["expiresIn"]))
                }
                _LOGGER.debug("New account added with the username %s", user_input['username'])
                return self.async_create_entry(title=user_input['username'].lower(), data=account)
            except CannotConnect:
                errors["base"] = "auth"
            except ValueError as error:
                errors["base"] = "err"
                _LOGGER.debug('Login failed: %s', error)
        if len(API_SERVERS) == 0 or len(API_COUNTRY) == 0 or len(API_TIMEZONE) == 0:
            API_SERVERS.clear()
            API_COUNTRY.clear()
            API_TIMEZONE.clear()
            async with aiohttp.ClientSession() as session:
                async with session.post(url=API_REGION_SERVERS) as response:
                    result = await response.json()
            for country_api in result:
                API_SERVERS.append([list(country_api.values())[2].upper(), list(country_api.values())[1]])
                API_COUNTRY.append([list(country_api.values())[2].upper(), list(country_api.values())[3]])
                if list(country_api.values())[2].upper() in list(dict(country_timezones.items()).keys()):
                    for timezone in dict(country_timezones.items())[list(country_api.values())[2].upper()]:
                        API_TIMEZONE.append([list(country_api.values())[2].upper(), timezone])
        STEP_USER_DATA_SCHEMA = vol.Schema(
            {
                vol.Required("username"): TextSelector(TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="username")),
                vol.Required("password"): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")),
                vol.Required("country", default=dict(API_COUNTRY).get(str(Locale(get_country_code(str(tzlocal.get_localzone())).replace('_', '-').upper())))): vol.In(sorted(list(dict(API_COUNTRY).values()))),
                vol.Required("timezone", default=dict(API_TIMEZONE).get(str(Locale(get_country_code(str(tzlocal.get_localzone())).replace('_', '-').upper())))): vol.In(sorted(list(dict(API_TIMEZONE).values()))),
            }
        )
        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)
    
class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""