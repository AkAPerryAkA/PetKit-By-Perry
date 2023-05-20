from .Core import *
from .config_flow import *
from .Account import *
from .Device import *

def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    
    # Return boolean to indicate that initialization was successful.
    return True