class Device:
    def __init__(
            self,
            Account,
            DeviceRaw,
    ):
        self._Account = Account
        self._Data_Device = DeviceRaw
        self._Type = DeviceRaw['type']
        self._Added = DeviceRaw['data']['createdAt']
        self._Name = DeviceRaw['data']['name']
        self._ID = DeviceRaw['data']['id']
        self._Firmware = DeviceRaw['data']['firmware']
        self._Description = DeviceRaw['data']['desc']
        if 'workState' in DeviceRaw['data']['status']:
            self._State = str(DeviceRaw['data']['status']['workState']['workMode']).replace('0', 'Cleaning').replace('9', 'Maintainance')
        else:
            self._State = 'Normal'
        self.updateDeviceInfo
    @property
    def updateDeviceData(self):
        Param = {
            "id": self._ID,
        }
        Result = sendRequest(self._Account, self._Account._TimeZone, self._Account._Locale, self._Account._API_SERVER + API_DEVICES_PATH, Param, self._Account._Token)['devices'][0]
        self._Data_Device = Result
        self._Type = Result['type']
        self._Added = Result['data']['createdAt']
        self._Name = Result['data']['name']
        self._ID = Result['data']['id']
        self._Firmware = Result['data']['firmware']
        self._Description = Result['data']['desc']
        if 'workState' in Result['data']['status']:
            self._State = str(Result['data']['status']['workState']['workMode']).replace('0', 'Cleaning').replace('9', 'Maintainance')
        else:
            self._State = 'Normal'
    @property
    def updateDeviceInfo(self):
        Param = {
            "deviceId": self._ID,
            "days": 1,
        }
        Result = sendRequest(self._Account, self._Account._TimeZone, self._Account._Locale, self._Account._API_SERVER + self._Type.lower() + API_DEVICE_DETAILS, Param, self._Account._Token)[0]
        self._Data_Detailed = Result
        if self._Type == "T4":
            self._Information = {
                'Wifi_MacAddress': Result['mac'],
                'BT_MacAddress': Result['btMac'],
                'SerialNumber': Result['sn'],
                'SecretKey': Result['secret'],
                'Settings': {
                    'Notify_FullBox': str(Result['settings']['litterFullNotify']).replace('0', 'False').replace('1', 'True'),
                    'Notify_LowSand': str(Result['settings']['lackSandNotify']).replace('0', 'False').replace('1', 'True'),
                    'Notify_Cleaned': str(Result['settings']['workNotify']).replace('0', 'False').replace('1', 'True'),
                    'Notify_InUse': str(Result['settings']['petInNotify']).replace('0', 'False').replace('1', 'True'),
                    'Notify_SprayLiquidLow': str(Result['settings']['lackLiquidNotify']).replace('0', 'False').replace('1', 'True'),
                    'Notify_DeodorantLow': str(Result['settings']['deodorantNotify']).replace('0', 'False').replace('1', 'True'),
                    'Notify_Weight': str(Result['settings']['weightPopup']).replace('0', 'False').replace('1', 'True'),
                    'SandType': str(Result['settings']['sandType']).replace('1', 'Bentonite').replace('2', 'Tofu').replace('3', 'Mixed'),
                    'ManualLock': str(Result['settings']['manualLock']).replace('0', 'False').replace('1', 'True'),
                    'AllowDump': str(Result['settings']['dumpSwitch']).replace('0', 'False').replace('1', 'True'),
                    'BaseWeight': Result['settings']['lightest']
                },
                'SmartSettings': {
                    'KittenMode': str(Result['settings']['kitten']).replace('0', 'False').replace('1', 'True'),
                    'AutoClean': str(Result['settings']['autoWork']).replace('0', 'False').replace('1', 'True'),
                    'CleanAfter': str(Result['settings']['fixedTimeClear'])+'m',
                    'AvoidRepeatClean': str(Result['settings']['avoidRepeat']).replace('0', 'False').replace('1', 'True'),
                    'DoNotCleanAfter': str(str(str(Result['settings']['autoIntervalMin']).replace('0', 'False'))+'m').replace('Falsem', 'False'),
                    'AvoidLightClean': str(Result['settings']['underweight']).replace('0', 'False').replace('1', 'True'),
                    'DeepClean': str(Result['settings']['deepClean']).replace('0', 'False').replace('1', 'True'),
                    'AutoSpray': str(Result['settings']['autoRefresh']).replace('0', 'False').replace('1', 'True'),
                    'SprayAfter': str(Result['settings']['fixedTimeRefresh'])+'m',
                    'DeepSpray': str(Result['settings']['deepRefresh']).replace('0', 'False').replace('1', 'True'),
                    'QuietMode': str(Result['settings']['disturbMode']).replace('0', 'False').replace('1', 'True'),
                    'QuietTime': Result['settings']['disturbRange']
                },
                'State': {
                    'Power': str(Result['state']['power']).replace('0', 'Off').replace('1', 'On'),
                    'Wireless': {
                        'Name': Result['state']['wifi']['ssid'],
                        'Broadcast': Result['state']['wifi']['bssid'],
                        'Strength': Result['state']['wifi']['rsq'],
                    },
                    'SandWeight': Result['state']['sandWeight'],
                    'SandPercentage': Result['state']['sandPercent'],
                    'SandLow': Result['state']['sandLack'],
                    'DeodorantLeft': str(Result['state']['deodorantLeftDays'])+' Days',
                    'BoxFull': Result['state']['boxFull'],
                    'TimesUsed': Result['state']['usedTimes'],
                    'InUseTime': Result['state']['petInTime'],
                    'PetError': Result['state']['petError']
                },
                'Statistics': {
                    'lastOutTime': Result['lastOutTime'],
                    'petOutRecords': Result['petOutRecords'],
                    'inTimes': Result['inTimes'],
                    'totalTime': Result['totalTime'],
                    'maintenanceTime': Result['maintenanceTime']
                }
            }
            if Result['settings']['disturbMode'] == 1:
                self._Information['SmartSettings'].update({
                    'QuietTime': Result['settings']['disturbRange']
                })
            if Result['withK3'] == 1:
                self._Information['State'].update({
                    'SprayLow': Result['state']['liquidLack'],
                    'SprayEmpty': Result['state']['liquidEmpty']
                })
                self._Information.update({
                    'SprayInstalled': 'True',
                    'SprayInformation': {
                        'ID': Result['k3Device']['id'],
                        'Mac': Result['k3Device']['mac'],
                        'SerialNumber': Result['k3Device']['sn'],
                        'SecretKey': Result['k3Device']['secret'],
                        'Name': Result['k3Device']['name'],
                        'Battery': Result['k3Device']['battery'],
                        'Liquid': Result['k3Device']['liquid'],
                        'IsSpraying': str(Result['k3Device']['refreshing']).replace('0', 'False').replace('1', 'True'),
                        'IsLighting': str(Result['k3Device']['lighting']).replace('0', 'False').replace('1', 'True'),
                        'BatteryVoltage': Result['k3Device']['voltage']
                    }
                })
            else:
                self._Information.update({
                    'SprayInstalled': False
                })
        else:
            self._Information = Result
    
    def Action_Execute(self, **kwargs):
        Param = {
            "id": self._ID,
            **kwargs,
        }
        print(Param)
        Result = sendRequest(self._Account, self._Account._TimeZone, self._Account._Locale, self._Account._API_SERVER + self._Type.lower() + API_DEVICE_ACTIONS, Param, self._Account._Token)
        if Result != 'success':
            raise ValueError(Result)
    @property
    def Toggle_Power(self):
        if self._Information['State']['Power'] == 'On':
            self.Action_Execute(type='power', kv='{ "power_action": 0 }')
        else:
            self.Action_Execute(type='power', kv='{ "power_action": 1 }')
    @property
    def Toggle_Maintainance(self):
        if self._State == 'Maintainance':
            self.Action_Execute(type='end', kv='{ "end_action": 9 }')
        elif self._State == 'Normal':
            self.Action_Execute(type='start', kv='{ "start_action": 9 }')
    @property
    def Toggle_Light(self):
        if self._Information['SprayInstalled'] == 'True':
            if self._Information['SprayInformation']['IsLighting'] == 'True':
                self.Action_Execute(type='end', kv='{ "end_action": 7 }')
            else:
                self.Action_Execute(type='start', kv='{ "start_action": 7 }')
    @property
    def Button_Clean(self):
        self.Action_Execute(type='start', kv='{ "start_action": 0 }')
    @property
    def Button_Spray(self):
        self.Action_Execute(type='start', kv='{ "start_action": 2 }')