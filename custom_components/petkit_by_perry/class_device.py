# MODULE IMPORT #
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.switch import (
    SwitchEntity,
    DOMAIN as SWITCH_ENTITY_DOMAIN,
)
from datetime import datetime
import logging
# VARIABLE/DEFINITION IMPORT #
from .const import API_DEVICE_DETAILS, DOMAIN, API_DEVICE_ACTIONS, API_SERVERS, API_COUNTRY
_LOGGER = logging.getLogger(__name__)

class PetKit_Device_T4(CoordinatorEntity):
    def __init__(self, hass: HomeAssistant, config, account, id):
        self._id = id
        super().__init__(account.co, context=account.devices[self._id]['data']['data']['name'])
        self.hass = hass
        self.config = config
        self.account = account
        self.hass_entities = {}
        self.hass_switch_entities = {}
        self.hass_button_entities = {}
        self.hass_select_entities = {}
    
    async def async__init__(self):
        self.hass_deviceinfo = DeviceInfo(
            config_entry_id = self.config.entry_id,
            identifiers = {(DOMAIN, self._id)},
            manufacturer = "PetKit",
            suggested_area = "Bathroom",
            name = self.name,
            model = self.type,
            sw_version = self.firmware,
        )
        self.hass_entities['switch'].append({
            'name': 'Power',
            'deviceinfo': self.hass_deviceinfo,
        })
        self.hass_entities['switch'].append({
            'name': 'Maintainance',
            'deviceinfo': self.hass_deviceinfo,
        })
        if self.device_detailed_data.get('withK3') == 1:
            self.hass_deviceinfo_addon = DeviceInfo(
                config_entry_id = self.config.entry_id,
                identifiers = {(DOMAIN, self.account.devices[self._id]['data_detailed']['k3Device']['id'])},
                manufacturer = "PetKit",
                suggested_area = "Bathroom",
                name = self.account.devices[self._id]['data_detailed']['k3Device']['name'],
                model = 'K3',
                sw_version = self.firmware,
                via_device = (DOMAIN, self._id),
            )
            self.hass_entities['switch'].append({
                'name': 'Light',
                'deviceinfo': self.hass_deviceinfo_addon,
            })
    
    @callback
    def _handle_coordinator_update(self) -> None:
        for name, value in self.hass_entities.items():
            match name:
                case 'switch':
                    for switch_name, switch_value in value:
                        switch_value['entity']._attr_is_on = self.get_attr(switch_name)
                        switch_value['entity']._is_on = self.get_attr(switch_name)
                        switch_value['entity'].async_write_ha_state()
                case _:
                    pass
    
    @property
    def type(self) -> str:
        return str(self.account.devices[self._id]['data']['type'])
    
    @property
    def created(self) -> str:
        return str(datetime.strptime(self.account.devices[self._id]['data']['data']['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ"))
    
    @property
    def name(self) -> str:
        return str(self.account.devices[self._id]['data']['data']['name'])
    
    @property
    def id(self) -> str:
        return str(self.account.devices[self._id]['data']['data']['id'])
    
    @property
    def firmware(self) -> str:
        return str(self.account.devices[self._id]['data']['data']['firmware'])
    
    @property
    def last_message(self) -> str:
        return str(self.account.devices[self._id]['data']['data']['status'])
    
    @property
    def state(self) -> str:
        if 'workState' in self.account.devices[self._id]['data']['data']['status']:
            return str(self.account.devices[self._id]['data']['data']['status']['workState']['workMode']).replace('0', 'Cleaning').replace('9', 'Maintainance')
        else:
            return str(self.account.devices[self._id]['data']['data']['status']['power']).replace('0', 'Off').replace('1', 'On')
    
    def get_attr(self, name):
        match name:
            case "Power":
                if self.state != 'Off':
                    return True
                return False
            case "Maintainance":
                if self.state == 'Maintainance':
                    return True
                return False
            case "Light":
                if self.account.devices[self._id]['data_detailed']['k3Device']['lighting'] == 'True':
                    return True
                return False
            case _:
                return None
    
    async def toggle(self, name) -> bool:
        match name:
            case "Power":
                if self.state != 'Off':
                    if await self.async_send_action(type='power', kv='{ "power_action": 0 }'):
                        self.account.devices[self._id]['data']['data']['status']['power'] = '0'
                        return True
                else:
                    if await self.async_send_action(type='power', kv='{ "power_action": 1 }'):
                        self.account.devices[self._id]['data']['data']['status']['power'] = '1'
                        return True
            case "Maintainance":
                if self.state == 'Maintainance':
                    if await self.async_send_action(type='end', kv='{ "end_action": 9 }'):
                        del self.account.devices[self._id]['data']['data']['status']['workState']
                        return True
                elif self.state == 'On':
                    if await self.async_send_action(type='start', kv='{ "start_action": 9 }'):
                        self.account.devices[self._id]['data']['data']['status']['workState'] = {
                            'workMode': '9',
                        }
                        return True
                return False
            case "Light":
                if self.account.devices[self._id]['data_detailed'].get('k3Device').get('lighting') == 'True':
                    if await self.async_send_action(type='end', kv='{ "end_action": 7 }'):
                        self.account.devices[self._id]['data_detailed']['k3Device']['lighting'] = 'False'
                        return True
                else:
                    if await self.async_send_action(type='start', kv='{ "start_action": 7 }'):
                        self.account.devices[self._id]['data_detailed']['k3Device']['lighting'] = 'True'
                        return True
            case _:
                return False
    
    async def button(self, name) -> bool:
        match name:
            case "Clean":
                if await self.async_send_action(type='start', kv='{ "start_action": 0 }'):
                    self.account.devices[self._id]['data']['data']['status']['workState'] = {
                        'workMode': '0',
                    }
                    return True
            case "Spray":
                if await self.async_send_action(type='start', kv='{ "start_action": 2 }'):
                    return True
            case _:
                return False
    
    async def async_send_action(self, **kwargs) -> bool:
        Param = {
            "id": self._id,
            **kwargs,
        }
        Result = await self.account.send_request(self.account.api_server + self.type.lower() + API_DEVICE_ACTIONS, Param, Token = True)
        if Result != 'success':
            return False
        return True
    
    async def toggle_power(self) -> bool:
        if self.state != 'Off':
            await self.async_send_action(type='power', kv='{ "power_action": 0 }')
        else:
            await self.async_send_action(type='power', kv='{ "power_action": 1 }')
    
    async def toggle_maintainance(self) -> bool:
        if self.state == 'Maintainance':
            return await self.async_send_action(type='end', kv='{ "end_action": 9 }')
        elif self.state == 'On':
            return await self.async_send_action(type='start', kv='{ "start_action": 9 }')