import datetime
import requests
from pytz import country_timezones

def getCountryCode(TimeZone):
    for countrycode in country_timezones:
        for timezone in country_timezones[countrycode]:
            if timezone == TimeZone:
                return countrycode
    return next(iter(country_timezones))

def sendRequest(Account, TimeZone, Locale, URL, Param = None, Token = None):
    if Token is not None:
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
    if Param is None:
        try:
            result = requests.post(URL, headers=Header, timeout=(2, 5))
        except ValueError as error:
            raise error
    else:
        try:
            result = requests.post(URL, data=Param, headers=Header, timeout=(2, 5))
        except ValueError as error:
            raise error
    if list(result.json().keys())[0] == 'result':
        if list(result.json()['result'])[0] == 'list':
            return result.json()['result']['list']
        else:
            return result.json()['result']
    elif list(result.json().keys())[0] == 'error':
        raise ValueError(result.json()['error']['msg'])
    else:
        raise ValueError('Unknown error!')
