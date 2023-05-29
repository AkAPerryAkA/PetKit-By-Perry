# IMPORTS #
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN
from .Account import Account
from .Device import Device

async def async_setup(hass, config):
    # Return boolean to indicate that initialization was successful.
    return True

async def async_setup_entry(hass, config_entry):
    _LOGGER.debug("setting up %s", config_entry.data['Username'])
    Acc = Account(hass, config_entry)
    if (await Acc.get_devices()):
        _LOGGER.debug("Found device(s) for %s", config_entry.data['Username'])
        return True
    return False
            