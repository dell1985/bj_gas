import logging
import datetime
import json
import asyncio

_LOGGER = logging.getLogger(__name__)

WEEK_QRY_URL = "https://zt.bjgas.com/bjgas-server/i/api/intelligent/getWeekQry?userCode="
STEP_QRY_URL = "https://zt.bjgas.com/bjgas-server/r/api?sysName=CCB&apiName=CM-MOB-IF07"
YEAR_QRY_URL = "https://zt.bjgas.com/bjgas-server/i/api/intelligent/getYearQry?userCode="
USER_INFO_URL = "https://zt.bjgas.com/bjgas-server/i/api/intelligent/queryUserInfo?userCode="


class AuthFailed(Exception):
    pass


class InvalidData(Exception):
    pass


class GASData:
    def __init__(self, session, token, user_code):
        self._session = session
        self._token = token
        self._user_code = user_code
        self._info = {}

    def common_headers(self):
        headers = {
            "Host": "zt.bjgas.com",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Language": "zh-cn, zh-Hans; q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 "
                          "(KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x1800072c) "
                          "NetType/WIFI Language/zh_CN",
            "Connection": "keep-alive",
            "Authorization": f"Bearer {self._token}"
        }
        return headers

    async def async_get_week(self, user_code):
        headers = self.common_headers()
        r = await self._session.get(WEEK_QRY_URL + user_code, headers=headers, timeout=10)
        if r.status == 200:
            result = json.loads(await r.read())
            if result["success"]:
                data = result["rows"][0]["infoList"]
                self._info[user_code]["daily_bills"] = data
            else:
                raise InvalidData(f"async_get_week error: {result}")
        else:
            raise InvalidData(f"async_get_week response status_code = {r.status}")

    async def async_get_year(self, user_code):
        headers = self.common_headers()
        r = await self._session.get(YEAR_QRY_URL + user_code, headers=headers, timeout=10)
        if r.status == 200:
            result = json.loads(await r.read())
            if result["success"]:
                data = result["rows"][0]["infoList"]
                self._info[user_code]["monthly_bills"] = data
            else:
                raise InvalidData(f"async_get_year error: {result}")
        else:
            raise InvalidData(f"async_get_year response status_code = {r.status}")

    async def async_get_userinfo(self, user_code):
        headers = self.common_headers()
        r = await self._session.get(USER_INFO_URL + user_code, headers=headers, timeout=10)
        if r.status == 200:
            result = json.loads(await r.read())
            if result["success"]:
                data = result["rows"][0]
                self._info[user_code]["last_update"] = data["fiscalDate"]
                self._info[user_code]["balance"] = float(data["remainAmt"])
                self._info[user_code]["battery_voltage"] = float(data["batteryVoltage"])
                self._info[user_code]["current_price"] = float(data["gasPrice"])
                self._info[user_code]["month_reg_qty"] = float(data["regQty"])
                self._info[user_code]["mtr_status"] = data["mtrStatus"]
            else:
                raise InvalidData(f"async_get_userinfo error: {result}")
        else:
            raise InvalidData(f"async_get_userinfo response status_code = {r.status}")

    async def async_get_step(self, user_code):
        headers = self.common_headers()
        headers["Content-Type"] = "application/json;charset=UTF-8"
        headers["Origin"] = "file://"
        json_date = {"CM-MOB-IF07": {"input": {"UniUserCode": f"{user_code}"}}}
        r = await self._session.post(STEP_QRY_URL, headers=headers, json=json_date, timeout=10)
        if r.status == 200:
            result = json.loads(await r.read())
            data = result["soapenv:Envelope"]["soapenv:Body"]["CM-MOB-IF07"]["output"]
            if float(data["Step1LeftoverQty"]) > 0:
                self._info[user_code]["current_level"] = 1
                self._info[user_code]["current_level_remain"] = float(data["Step1LeftoverQty"])
            else:
                self._info[user_code]["current_level"] = 2
                self._info[user_code]["current_level_remain"] = float(data["Step2LeftoverQty"])
            self._info[user_code]["year_consume"] = float(data["TotalSq"])
        else:
            raise InvalidData(f"async_get_step response status_code = {r.status}")

    async def async_get_data(self):
        self._info = {self._user_code: {}}
        tasks = [
            self.async_get_userinfo(self._user_code),
            self.async_get_week(self._user_code),
            self.async_get_year(self._user_code),
            self.async_get_step(self._user_code)
        ]
        await asyncio.wait(tasks)
        _LOGGER.debug(f"Data {self._info}")
        return self._info
