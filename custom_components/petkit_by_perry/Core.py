import datetime
import pytz
import tzlocal
import locale
import aiohttp
import re
from datetime import datetime, timedelta
from pytz import country_timezones

from .const import API_REGION_SERVERS, API_SERVERS, API_LANGUAGE, API_SERVER, API_LOGIN_PATH, API_COUNTRY

def getCountryCode(TimeZone):
    for countrycode in country_timezones:
        for timezone in country_timezones[countrycode]:
            if timezone == TimeZone:
                return countrycode.upper()
    return next(iter(country_timezones))

async def getAPIServers():
    result = await sendRequest(None, pytz.timezone(str(tzlocal.get_localzone())), API_REGION_SERVERS, None)
    API_SERVERS.clear()
    API_COUNTRY.clear()
    for CountryCode in result:
        API_SERVERS.append([list(CountryCode.values())[2].upper(), list(CountryCode.values())[1]])
        API_COUNTRY.append([list(CountryCode.values())[2].upper(), list(CountryCode.values())[3]])

async def getAPIToken(Username, Password, Country, TimeZone):
    TimeZone = pytz.timezone(TimeZone)
    Param = {
        "timezoneId": TimeZone.zone,
        "timezone": f"{round(TimeZone.seconds/60/60)}.0",
        "username": Username,
        "password": Password,
        "locale": locale.getdefaultlocale()[0],
        "encrypt": 1,
    }
    Result = sendRequest(None, TimeZone, API_SERVER + API_LOGIN_PATH, Param)
    Session = Result['session']
    _Token = Session["id"]
    _Token_Created = datetime.strptime(Session["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
    _Token_Expires = _Token_Created + timedelta(seconds = Session["expiresIn"])
    print("Session created succesfully!")

async def sendRequest(Account, TimeZone, URL, Param = None):
    if Account is not None:
        if Account._Token_Expires > datetime.now():
            await getAPIToken(None, None, None, None)
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
