class Account:
    def __init__(
            self,
            Username,
            Password,
            Country = None,
            TimeZone = None,
            Locale = None,
            Token = None,
            Token_Created = None,
            Token_Expires = None,
    ):
        self._Username = Username
        if re.findall(r"([a-fA-F\d]{32})", Password):
            self._Password = Password.lower()
        else:
            hash = hashlib.md5()
            hash.update(Password.encode("utf-8"))
            self._Password = hash.hexdigest()
        if Country is None:
            self._Country = str(tzlocal.get_localzone())
        else:
            self._Country = Country
        self._CountryCode = self.getCountryCode
        if TimeZone is None:
            self._TimeZone = str(tzlocal.get_localzone())
        else:
            self._TimeZone = TimeZone
        self._TimeZone = pytz.timezone(self._TimeZone)
        if Locale is None:
            self._Locale = locale.getdefaultlocale()
        else:
            self._Locale = Locale
        self._Token = Token
        self._Token_Created = Token_Created
        self._Token_Expires = Token_Expires
        self._API_SERVER_LIST = self.getRegionServers
        self._API_SERVER = self.getAPIServer
        self._Devices = []
        self.getToken
        if self._Token != None:
            self.getDevices
    @property
    def getCountryCode(self):
        for countrycode in country_timezones:
            for timezone in country_timezones[countrycode]:
                if timezone == self._Country:
                    return countrycode
        return next(iter(country_timezones))
    @property
    def getRegionServers(self):
        try:
            return sendRequest(self, self._TimeZone, self._Locale, API_REGION_SERVERS)["list"]
        except:
            return None
    @property
    def getAPIServer(self):
        for item in self._API_SERVER_LIST:
            if item['id'] == self._CountryCode:
                return item['gateway']
        return self._API_SERVER_LIST[0]['gateway']
    @property
    def getToken(self):
        Param = {
            "timezoneId": self._TimeZone.zone,
            "timezone": f"{round(self._TimeZone._utcoffset.seconds/60/60)}.0",
            "username": self._Username,
            "password": self._Password,
            "locale": self._Locale,
            "encrypt": 1,
        }
        Result = sendRequest(self, self._TimeZone, self._Locale, self._API_SERVER + API_LOGIN_PATH, Param)
        Session = Result['session']
        self._Token = Session["id"]
        self._Token_Created = datetime.strptime(Session["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self._Token_Expires = self._Token_Created + timedelta(seconds = Session["expiresIn"])
        print("Session created succesfully!")
    @property
    def getDevices(self):
        for NewDevice in sendRequest(self, self._TimeZone, self._Locale, self._API_SERVER + API_DEVICES_PATH, None, self._Token)["devices"]:
            self._Devices.append(Device(self, NewDevice))