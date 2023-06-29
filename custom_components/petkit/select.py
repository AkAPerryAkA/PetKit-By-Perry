# MODULE IMPORT #
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.select import (
    SelectEntity,
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
        for name, value in dev.hass_select_entities.items():
            entity = PetKitSelect(dev, name, value['deviceinfo'])
            async_add_entities([entity])
            value['entity'] = entity
            value['hass_entity'] = entity_registry.async_get(f"{value['deviceinfo'].name}_{name}")

class PetKitSelect(SelectEntity):
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

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        