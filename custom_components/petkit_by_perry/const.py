from datetime import timedelta

API_LOGIN_PATH = "user/login"
API_DEVICES_PATH = "discovery/device_roster"
API_DEVICE_DETAILS = "/owndevices"
API_DEVICE_ACTIONS = "/controlDevice"
API_REGION_SERVERS = "https://passport.petkt.com/v1/regionservers"
API_SCAN_INTERVAL = timedelta(minutes=2)
API_SERVERS = []
API_COUNTRY = []
API_TIMEZONE = []
DOMAIN = "petkit_by_perry"
SUPPORTED_DOMAINS = [
    'sensor',
    'binary_sensor',
    'switch',
    'select',
]