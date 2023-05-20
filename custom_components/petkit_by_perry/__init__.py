# IMPORTS #
import requests
import pytz
from pytz import country_timezones
import hashlib
from datetime import datetime, time, timedelta
import re
import json
import locale
import tzlocal
import copy
import logging
import hashlib
from homeassistant.core import HomeAssistant
from homeassistant import config_entries
from homeassistant.const import *
from homeassistant.components import persistent_notification
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.storage import Store
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
import homeassistant.helpers.config_validation as cv
from asyncio import TimeoutError
from aiohttp import ClientConnectorError, ContentTypeError
import voluptuous as vol

from .const import *
from .Core import *
from .config_flow import *
from .Account import *
from .Device import *

for CountryCode in await sendRequest(None, pytz.timezone(str(tzlocal.get_localzone())), locale.getdefaultlocale(), API_REGION_SERVERS)["list"]:
    API_SERVERS.append([list(CountryCode.values())[2], list(CountryCode.values())[1]])

def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    
    # Return boolean to indicate that initialization was successful.
    return True