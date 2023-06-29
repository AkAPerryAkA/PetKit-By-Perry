# MODULE IMPORT #
import datetime
import pytz
import tzlocal
from datetime import datetime, timedelta
from pytz import country_timezones
import hashlib
import re
import locale
import aiohttp
import logging
from homeassistant.core import HomeAssistant, CALLBACK_TYPE, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from collections.abc import Callable
from typing import Any
# VARIABLE/DEFINITION IMPORT #
from .const import DOMAIN, API_SERVERS, API_COUNTRY, API_TIMEZONE, API_REGION_SERVERS, PLATFORMS, API_SCAN_INTERVAL, DEVICES
from .class_account import PetKit_Account
from .class_coordinator import PetKit_Coordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    API_SERVERS.clear()
    API_COUNTRY.clear()
    API_TIMEZONE.clear()
    async with aiohttp.ClientSession() as session:
        async with session.post(url=API_REGION_SERVERS) as response:
            result = await response.json()
    for country_api in result:
        API_SERVERS.append([list(country_api.values())[2].upper(), list(country_api.values())[1]])
        API_COUNTRY.append([list(country_api.values())[2].upper(), list(country_api.values())[3]])
        if list(country_api.values())[2].upper() in list(dict(country_timezones.items()).keys()):
            for timezone in dict(country_timezones.items())[list(country_api.values())[2].upper()]:
                API_TIMEZONE.append([list(country_api.values())[2].upper(), timezone])
    return True

async def async_setup_entry(hass, config_entry):
    _LOGGER.debug("setting up %s", config_entry.data['Username'])
    co = PetKit_Coordinator(hass)
    Acc = PetKit_Account(hass, config_entry, co)
    if (await Acc.get_devices()) is True:
        _LOGGER.debug("Found device(s) for %s", config_entry.data['Username'])
        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
        await co.async_refresh()
        return True
    return False