import datetime
import pytz
import tzlocal
from datetime import datetime, timedelta
from pytz import country_timezones
import hashlib
import re
import locale
import aiohttp

from .const import API_REGION_SERVERS, API_SERVERS, API_LOGIN_PATH, API_COUNTRY, API_TIMEZONE

def getCountryCode(TimeZone):
    for countrycode in country_timezones:
        for timezone in country_timezones[countrycode]:
            if timezone == TimeZone:
                return countrycode.upper()
    return next(iter(country_timezones))

async def getAPIServers():
    API_SERVERS.clear()
    API_COUNTRY.clear()
    API_TIMEZONE.clear()
    for CountryCode in (await sendRequest(None, pytz.timezone(str(tzlocal.get_localzone())), API_REGION_SERVERS, None)):
        API_SERVERS.append([list(CountryCode.values())[2].upper(), list(CountryCode.values())[1]])
        API_COUNTRY.append([list(CountryCode.values())[2].upper(), list(CountryCode.values())[3]])
        if list(CountryCode.values())[2].upper() in list(dict(country_timezones.items()).keys()):
            for TimeZone in dict(country_timezones.items())[list(CountryCode.values())[2].upper()]:
                API_TIMEZONE.append([list(CountryCode.values())[2].upper(), TimeZone])

async def getAPIToken(Username, Password, Country, TimeZone):
    if re.findall(r"([a-fA-F\d]{32})", Password):
        Password = Password.lower()
    else:
        hash = hashlib.md5()
        hash.update(Password.encode("utf-8"))
        Password = hash.hexdigest()
    TimeZone = pytz.timezone(TimeZone)
    Param = {
        "timezoneId": TimeZone.zone,
        "timezone": f"{round(TimeZone._utcoffset.seconds/60/60)}.0",
        "username": Username,
        "password": Password,
        "locale": locale.getdefaultlocale()[0],
        "encrypt": 1,
    }
    try:
        Result = await sendRequest(None, TimeZone, dict(API_SERVERS).get(Country) + API_LOGIN_PATH, Param)
        Account = {
            "UserID": Result['user']['account']['userId'],
            "Username": Username,
            "Password": Password,
            "Country": Country,
            "TimeZone": str(TimeZone),
            "Token": Result['session']['id'],
            "Token_Created": str(datetime.strptime(Result['session']["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")),
            "Token_Expires": str(datetime.strptime(Result['session']["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(seconds = Result['session']["expiresIn"]))
        }
        print("Session created succesfully!")
        return Account
    except:
        return False

async def sendRequest(Account, TimeZone, URL, Param = None):
    if Account is not None:
        if Account.token_expires > datetime.now():
            await getAPIToken(None, None, None, None)
        Header = {
            "X-Session": Account.token,
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
        "X-Locale": locale.getdefaultlocale()[0].replace("-", "_"),
    })
    if Param is None:
        try:
            async with aiohttp.ClientSession(headers=Header) as session:
                async with session.get(url=URL) as response:
                    result = await response.json()
        except ValueError as error:
            raise error
    else:
        try:
            async with aiohttp.ClientSession(headers=Header) as session:
                async with session.get(url=URL, params=Param) as response:
                    result = await response.json()
        except ValueError as error:
            raise error
    if list(result.keys())[0] == 'result':
        if list(result['result'])[0] == 'list':
            return result['result']['list']
        else:
            return result['result']
    elif list(result.keys())[0] == 'error':
        raise ValueError(result['error']['msg'])
    else:
        raise ValueError('Unknown error!')
