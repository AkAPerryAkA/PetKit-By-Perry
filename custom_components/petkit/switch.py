# MODULE IMPORT #
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.switch import (
    SwitchEntity,
    DOMAIN as ENTITY_DOMAIN,
)
import logging
# VARIABLE/DEFINITION IMPORT #
from .const import DOMAIN, DEVICES
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    entity_registry = er.async_get(hass)
    _LOGGER.debug("Setting up platform %s", ENTITY_DOMAIN)
    for username, dev in DEVICES.items():
        _LOGGER.debug("Working on device %s on platform %s", dev.name, ENTITY_DOMAIN)
        for name, value in dev.hass_switch_entities.items():
            entity = PetKitSwitch(dev, name, value['deviceinfo'])
            async_add_entities([entity])
            value['entity'] = entity
            value['hass_entity'] = entity_registry.async_get(f"{value['deviceinfo'].name}_{name}")

class PetKitSwitch(SwitchEntity):
    _attr_has_entity_name = True
    
    def __init__(self, device, name, deviceinfo):
        self.device = device
        self.deviceinfo = deviceinfo
        self.entity_name = name
        self._attr_unique_id = name
        self._attr_name = name
    
    @property
    def device_info(self) -> DeviceInfo:
        return self.deviceinfo
    
    @property
    def unique_id(self):
        return self._attr_unique_id
    
    @property
    def is_on(self):
        return self.device.get_attr(self.entity_name)

    async def async_turn_on(self):
        await self.async_toggle()

    async def async_turn_off(self):
        await self.async_toggle()

    async def async_toggle(self):
        return await self.device.toggle(self.entity_name)
        