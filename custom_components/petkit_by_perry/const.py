from datetime import timedelta

API_LOGIN_PATH = "user/login"
API_DEVICES = "discovery/device_roster"
API_DEVICE_DETAILS = "/owndevices"
API_DEVICE_ACTIONS = "/controlDevice"
API_REGION_SERVERS = "https://passport.petkt.com/v1/regionservers"
API_SCAN_INTERVAL = timedelta(seconds=10)
API_SERVERS = []
API_COUNTRY = []
API_TIMEZONE = []
DOMAIN = "petkit"
DEVICES = {}
PLATFORMS = (
    "switch",
    "select",
)