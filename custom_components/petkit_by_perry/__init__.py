# IMPORTS #
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN
from .Core import *
from .config_flow import *
from .Account import Account
from .Device import *

async def async_setup(hass: HomeAssistant, hass_config: dict):
    _LOGGER.info('Starting setup for {}'.format(DOMAIN))
    hass.data.setdefault(DOMAIN, {})
    config = hass_config.get(DOMAIN) or {}
    hass.data[DOMAIN]['config'] = config
    hass.data.setdefault(DOMAIN, {})
    config = hass_config.get(DOMAIN) or {}
    if config is {}:
        _LOGGER.warning('No config found for {}'.format(DOMAIN))
        return False
    for Acc in config:
        _LOGGER.info('setting up {} in {}'.format(Acc.get('Username'), DOMAIN))
        t_acc = Account(hass, Acc)
        if t_acc.update_token():
            t_acc.get_devices()
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    device = PetKit(hass, entry.data[DOMAIN])
    await device.async_setup()

class PetKit:
    def __init__(self, hass: HomeAssistant, config: dict):
        self._config = config
        self.hass = hass
    async def async_setup(self) -> bool:
        self.hass.data.setdefault(DOMAIN, {})
        config = self._config.get(DOMAIN) or {}
        if config is None:
            return False
        for Acc in config:
            t_acc = Account(self.hass, Acc)
            if t_acc.update_token():
                t_acc.get_devices()
            