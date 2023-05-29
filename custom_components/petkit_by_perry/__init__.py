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
    _LOGGER.debug("setting up %s in %s", config_entry.data['Username'], DOMAIN)
    Acc = Account(hass, config_entry)
    if Acc.update_token():
        Acc.get_devices()
    return True
            