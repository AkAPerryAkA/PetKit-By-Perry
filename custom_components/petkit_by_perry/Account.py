"""
Account = {
    "UserID": Result['user']['account']['userId'],
    "Username": Username,
    "Password": Password,
    "Country": Country,
    "TimeZone": str(TimeZone),
    "Token": Result['session']['id'],
    "Token_Created": str(datetime.strptime(Result['session']["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")),
    "Token_Expires": str(datetime.strptime(Result['session']["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(seconds = Result['session']["expiresIn"]))
}
"""
import re
import hashlib
import pytz
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
import locale
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

from .const import API_SERVERS, API_SERVER, API_LOGIN_PATH, API_DEVICES_PATH
from .Core import CannotConnect
from .Device import Device

class Account:
    def __init__(self, hass: HomeAssistant, config: dict):
        self._config = config
        self.hass = hass
        if self._config.get('Devices') is None:
            self._config.update({
                'Devices': {}
            })
    
    @property
    def username(self) -> str:
        return self._config.get('Username')
    
    @property
    def password(self) -> str:
        return self._config.get('Password')
    
    @property
    def country(self) -> str:
        return self._config.get('Country')
    
    @property
    def timezone(self) -> str:
        return self._config.get('TimeZone')
    
    @property
    def token(self) -> str:
        return self._config.get('Token')
    
    @property
    def token_created(self) -> str:
        return self._config.get('Token_Created')
    
    @property
    def token_expires(self) -> str:
        return self._config.get('Token_Expires')
    
    def update_config(self, item, val):
        self._config[item] = val
    
    async def update_token(self) -> bool:
        if re.findall(r"([a-fA-F\d]{32})", self.password):
            self.password = self.password.lower()
        else:
            hash = hashlib.md5()
            hash.update(self.password.encode("utf-8"))
            self.password = hash.hexdigest()
        self.timezone = pytz.timezone(self.timezone)
        Param = {
            "timezoneId": self.timezone.zone,
            "timezone": f"{round(self.timezone._utcoffset.seconds/60/60)}.0",
            "username": self.username,
            "password": self.password,
            "locale": locale.getdefaultlocale()[0],
            "encrypt": 1,
        }
        try:
            result = await self.send_request(dict(API_SERVERS).get(self.country) + API_LOGIN_PATH, Param)
            self.update_config('Token', result['session']['id'])
            self.update_config('Token_Created', str(datetime.strptime(result['session']["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")))
            self.update_config('Token_Expires', str(datetime.strptime(result['session']["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(seconds = result['session']["expiresIn"])))
            _LOGGER.debug("Update token for %s success", self.username)
            return True
        except ValueError as error:
            _LOGGER.debug("Update token for %s failed: %s", self.username, error)
            return False
    
    async def send_request(self, URL, Param = None, Token = False) -> dict:
        if Token is True:
            if self.token_expires > datetime.now():
                await self.update_token()
            Header = {
                "X-Session": self.token,
            }
        else:
            Header = {}
        self.timezone = pytz.timezone(self.timezone)
        Header.update({
            "User-Agent": "PETKIT/7.26.1 (iPhone; iOS 14.7.1; Scale/3.00)",
            "X-Timezone": f"{round(self.timezone._utcoffset.seconds/60/60)}.0",
            "X-Api-Version": "7.26.1",
            "X-Img-Version": "1",
            "X-TimezoneId": self.timezone.zone,
            "X-Client": "ios(14.7.1;iPhone13,4)",
            "X-Locale": locale.getdefaultlocale()[0].replace("-", "_"),
        })
        try:
            async with aiohttp.ClientSession(headers=Header) as session:
                async with session.get(url=URL, params=Param) as response:
                    result = await response.json()
        except ValueError as error:
            _LOGGER.debug("API request for %s failed: %s", self.username, error)
            return None
        if list(result.keys())[0] == 'result':
            _LOGGER.debug("API returned results for %s", self.username)
            if list(result['result'])[0] == 'list':
                return result['result']['list']
            else:
                return result['result']
        elif list(result.keys())[0] == 'error':
            _LOGGER.debug("API returned error for %s: %s", self.username, result['error']['msg'])
            raise CannotConnect(result['error']['msg'])
        else:
            _LOGGER.debug("Unknown API response for %s: %s", self.username, URL)
            raise Exception("Unknown API response")
    
    async def get_devices(self) -> bool:
        for NewDevice in (await self.send_request(API_SERVER + API_DEVICES_PATH, Token = True))["devices"]:
            if NewDevice['data']['id'] not in self._config['Devices']:
                self._config['Devices'].update({
                    NewDevice['data']['id']: {
                        'Type': NewDevice['type'],
                        'Added': NewDevice['data']['createdAt'],
                        'Name': NewDevice['data']['name'],
                        'Firmware': NewDevice['data']['firmware'],
                        'Description': NewDevice['data']['desc']
                    }
                })
                if 'workState' in NewDevice['data']['status']:
                    self._config['Devices'][NewDevice['data']['id']].update({
                        'State': str(NewDevice['data']['status']['workState']['workMode']).replace('0', 'Cleaning').replace('9', 'Maintainance')
                    })
                else:
                    self._config['Devices'][NewDevice['data']['id']].update({
                        'State': 'Normal'
                    })
                _LOGGER.info("Found new device for %s with ID %s and type %s", self.username, NewDevice['data']['id'], NewDevice['type'])
            #Device(self.hass, self._config, self._config['Devices'][NewDevice['data']['id']])
        return True