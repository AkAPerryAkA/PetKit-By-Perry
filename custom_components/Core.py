import requests
import pytz
from pytz import country_timezones
import hashlib
from datetime import datetime, time, timedelta
import re
import json
import locale
import tzlocal

API_LOGIN_PATH = "user/login"
API_DEVICES_PATH = "discovery/device_roster"
API_REGION_SERVERS = "https://passport.petkt.com/v1/regionservers"

def sendRequest(Account, TimeZone, Locale, URL, Param = None, Token = None):
    if Token != None:
        if Account._Token_Expires > datetime.now():
            Account.getToken
        Header = {
            "X-Session": Account._Token,
        }
    else:
        Header = {}
    Header.update({
        "User-Agent": "PETKIT/7.26.1 (iPhone; iOS 14.7.1; Scale/3.00)",
        "X-Timezone": f"{round(TimeZone._utcoffset.seconds/60/60)}.0",
        "X-Api-Version": "7.26.1",
        "X-Img-Version": "1",
        "X-TimezoneId": TimeZone.zone,
        "X-Client": "ios(14.7.1;iPhone13,4)",
        "X-Locale": str(Locale).replace("-", "_"),
    })
    if Param == None:
        try:
            Result = requests.post(URL, headers=Header)
        except ValueError as e:
            raise e
    else:
        try:
            Result = requests.post(URL, data=Param, headers=Header)
        except ValueError as e:
            raise e
    if list(Result.json().keys())[0] == 'result':
        return Result.json()['result']
    elif list(Result.json().keys())[0] == 'error':
        raise ValueError(Result.json()['error']['msg'])
    else:
        raise ValueError('Unknown error!')