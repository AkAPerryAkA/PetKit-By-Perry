# IMPORTS #
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN
from .Account import Account
from .Device import Device

async def async_setup_entry(hass, config):
    config = config.get(DOMAIN) or {}
    if config is {}:
        _LOGGER.debug("No config found for %s", DOMAIN)
        return False
    for Acc in config:
        _LOGGER.debug("setting up %s in %s", Acc.get('Username'), DOMAIN)
        t_acc = Account(hass, Acc)
        if t_acc.update_token():
            t_acc.get_devices()
    return True
            