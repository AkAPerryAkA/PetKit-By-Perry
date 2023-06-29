# MODULE IMPORT #
from homeassistant.core import HomeAssistant
from datetime import datetime
import logging
# VARIABLE/DEFINITION IMPORT #
from .const import API_SERVERS, API_COUNTRY, DOMAIN, PLATFORMS
from .class_coordinator import PetKit_Coordinator
_LOGGER = logging.getLogger(__name__)

class PetKit_Account:
    def __init__(self, hass: HomeAssistant, config):
        self.hass = hass
        self.config = config
        self.devices = {}
        self.coordinator = PetKit_Coordinator(hass, self)
    
    @property
    def username(self) -> str:
        return self.config.data.get('Username')
    
    @property
    def password(self) -> str:
        return self.config.data.get('Password')
    
    @property
    def country(self) -> str:
        return self.config.data.get('Country')
    
    @property
    def timezone(self) -> str:
        return self.config.data.get('TimeZone')
    
    @property
    def api_server(self) -> str:
        return dict(API_SERVERS).get(list(dict(API_COUNTRY).keys())[list(dict(API_COUNTRY).values()).index(self.country)])
    
    @property
    def token(self) -> str:
        return self.config.data.get('Token')
    
    @property
    def token_created(self) -> str:
        return str(datetime.strptime(self.config.data.get('Token_Created'), "%Y-%m-%d %H:%M:%S.%f"))
    
    @property
    def token_expires(self) -> str:
        return str(datetime.strptime(self.config.data.get('Token_Expires'), "%Y-%m-%d %H:%M:%S.%f"))
    
    @property
    def devices_data(self) -> dict:
        return self.config.data.get('Devices_Data')
    
    async def async_setup(self) -> bool:
        await self.coordinator.async_refresh()
        await self.hass.config_entries.async_forward_entry_setups(self.config, PLATFORMS)
        return True

    async def async_migrate_entry(self, hass, config_entry, item, val) -> bool:
        _LOGGER.debug("[%s]: Updating %s value", config_entry.version, item)
        new = {**config_entry.data}
        new[item] = val
        hass.config_entries.async_update_entry(config_entry, data=new)
        return True
    
    async def async_get_current_config(self):
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.entry_id == self.config.entry_id:
                return entry
    
    async def async_update_config(self, item, val):
        if (await self.async_migrate_entry(self.hass, self.config, item, val)) is True:
            self.config = await self.async_get_current_config()
            _LOGGER.debug("Retreive new config for %s success", item)
        else:
            _LOGGER.debug("Retreive new config for %s failed", item)