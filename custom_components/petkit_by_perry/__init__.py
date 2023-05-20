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

from .const import *
from .Core import *
from .config_flow import *
from .Account import *
from .Device import *

def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    
    # Return boolean to indicate that initialization was successful.
    return True