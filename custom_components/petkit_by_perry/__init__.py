# IMPORTS #
import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN
from .Core import *
from .config_flow import *
from .Account import Account
from .Device import *

async def async_setup(hass: HomeAssistant, hass_config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    config = hass_config.get(DOMAIN) or {}
    if config is None:
        return False
    for Acc in config:
        t_acc = Account(hass, Acc)
        if t_acc.update_token():
            t_acc.get_devices()
            