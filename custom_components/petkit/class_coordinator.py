# MODULE IMPORT #
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant import exceptions
from datetime import datetime, timedelta
import aiohttp
import logging
import locale
import pytz
# VARIABLE/DEFINITION IMPORT #
from .const import DOMAIN, API_SERVERS, API_COUNTRY, API_TIMEZONE, API_REGION_SERVERS, PLATFORMS, API_SCAN_INTERVAL, DEVICES, API_LOGIN_PATH, API_DEVICE_DETAILS, API_DEVICES
from .class_account import PetKit_Account
from .class_device import PetKit_Device_T4
_LOGGER = logging.getLogger(__name__)

class PetKit_Coordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, account: PetKit_Account):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=API_SCAN_INTERVAL)
        self.hass = hass
        self.account = account
        _LOGGER.debug("Coordinator has started!")
    
    def async_add_listener(self, coordinator, context): # ?????
        _LOGGER.debug("Coordinator listener: %s", str(coordinator))
        _LOGGER.debug("Context listener: %s", str(context))

    async def _async_update_data(self):
        _LOGGER.debug("Update started!")
        devices_found = await self.async_get_devices()
        devices_current = self.account.devices
        if len(devices_current) == 0:
            devices_current = devices_found
        else:
            # UPDATE EXISTING DEVICES
            for dev_id, value in devices_current.items():
                if devices_found[dev_id] is not None:
                    devices_current[dev_id]['data'] = devices_found[dev_id]['data']
                    devices_current[dev_id]['data_detailed'] = devices_found[dev_id]['data_detailed']
                    devices_current[dev_id]['last_update'] = devices_found[dev_id]['last_update']
                else:
                    # REMOVE DEVICE WITH ENTITY
                    pass
            # ADD NEW DEVICES
            for dev_id, value in devices_found.items():
                if devices_current[dev_id] is None:
                    match value['data']['type'].upper():
                        case 'T4':
                            value['hass_device'] = PetKit_Device_T4(self.hass, self.account.config, self.account, value['data']['data']['id'])
                        case _:
                            _LOGGER.debug("The device for %s with ID %s and type %s is not supported :(", self.account.username, value['data']['data']['id'], value['data']['type'])
                    devices_current[dev_id] = value
        self.account.devices = devices_current
        await self.account.async_update_config('Devices_Data', devices_current)
        _LOGGER.debug("Update completed!")
    
    async def async_get_devices(self) -> dict:
        _LOGGER.debug("Requesting device(s) from %s", self.account.username)
        devices_found = {}
        for device in (await self.send_request(self.account.api_server + API_DEVICES, Token = True))["devices"]:
            _LOGGER.debug("Found device for %s with ID %s and type %s", self.account.username, device['data']['id'], device['type'])
            device_detailed = await self.send_request(self.account.api_server + device['type'].lower() + API_DEVICE_DETAILS, { "deviceId": device['data']['id'], "days": 1 }, token = True)
            match device['type'].upper():
                case "T4":
                    devices_found[device['data']['id']] = {
                        'data': device,
                        'data_detailed': device_detailed,
                        'last_update': str(datetime.utcnow()),
                    }
                case _:
                    pass
        return devices_found
    
    async def async_update_token(self) -> bool:
        _LOGGER.debug("Requesting Token from %s", self.username)
        if issubclass(type(self.account.timezone), str):
            timezone = pytz.timezone(self.account.timezone)
        else:
            timezone = self.account.timezone
        param = {
            "timezoneId": timezone.zone,
            "timezone": f"{round(timezone._utcoffset.seconds/60/60)}.0",
            "username": self.account.username,
            "password": self.account.password,
            "locale": locale.getdefaultlocale()[0],
            "encrypt": 1,
        }
        _LOGGER.debug("Token for %s expired %s UTC", self.account.username, self.account.token_expires)
        try:
            result = await self.async_send_request(self.account.api_server + API_LOGIN_PATH, param)
            await self.account.async_update_config('Token', result['session']['id'])
            await self.account.async_update_config('Token_Created', str(datetime.strptime(result['session']["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")))
            await self.account.async_update_config('Token_Expires', str(datetime.strptime(result['session']["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(seconds = result['session']["expiresIn"])))
            _LOGGER.debug("Update token for %s success", self.account.username)
            _LOGGER.debug("Token expires: %s", self.account.token_expires)
            return True
        except ValueError as error:
            _LOGGER.debug("Update token for %s failed: %s", self.account.username, error)
            return False
    
    async def async_send_request(self, url, param = None, token = False) -> dict:
        if token is True:
            if datetime.strptime(self.account.token_expires, "%Y-%m-%d %H:%M:%S.%f") < datetime.utcnow():
                await self.async_update_token()
            header = {
                "X-Session": self.account.token,
            }
        else:
            header = {}
        timezone = self.account.timezone
        if issubclass(type(self.account.timezone), str):
            timezone = pytz.timezone(self.account.timezone)
        header.update({
            "User-Agent": "PETKIT/7.26.1 (iPhone; iOS 14.7.1; Scale/3.00)",
            "X-Timezone": f"{round(timezone._utcoffset.seconds/60/60)}.0",
            "X-Api-Version": "7.26.1",
            "X-Img-Version": "1",
            "X-TimezoneId": timezone.zone,
            "X-Client": "ios(14.7.1;iPhone13,4)",
            "X-Locale": locale.getdefaultlocale()[0].replace("-", "_"),
        })
        try:
            async with aiohttp.ClientSession(headers=header) as session:
                async with session.get(url=url, params=param) as response:
                    result = await response.json()
        except ValueError as error:
            _LOGGER.debug("API request for %s failed: %s", self.account.username, error)
            return None
        if list(result.keys())[0] == 'result':
            _LOGGER.debug("API returned results for %s", self.account.username)
            if list(result['result'])[0] == 'list':
                return result['result']['list']
            else:
                return result['result']
        elif list(result.keys())[0] == 'error':
            _LOGGER.debug("API returned error for %s: %s", self.account.username, result['error']['msg'])
            _LOGGER.debug("Token expires: %s", self.account.token_expires)
            raise CannotConnect(result['error']['msg'])
        else:
            _LOGGER.debug("Unknown API response for %s: %s", self.account.username, url)
            raise ValueError("Unknown API response")

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""