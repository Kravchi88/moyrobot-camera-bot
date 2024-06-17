import json
import aiohttp
import logging

from app.services.client_database.utils.phone import (
    format_phone,
    is_phone_correct,
    phone_to_text,
)


class TerminalSession:
    """
    Class that implements connection to terminal site
    In cookies saves session information which helps not to login every time when used

    Usage:
        terminal_session = TerminalSession(...)
        async with terminal_session as session:
            ...
    """

    def __init__(self, terminal_id: int, url: str, login: str, password: str) -> None:
        self.terminal_id = terminal_id
        self.url = url
        self.__login = login
        self.__password = password
        self.__login_url = url + "/Account/Login"
        self.__table_sales_url = url + "/Admin/_TableSales"
        self.__bonus_create_url = (
            url
            + "/Modules/ModulePartial_Post?ModuleUrl=http://localhost:8083&ActionUrl=BonusChanges/Create"
        )
        self.__cookie_jar = aiohttp.CookieJar()
        self._session = aiohttp.ClientSession(cookie_jar=self.__cookie_jar)

    async def __aenter__(self) -> "TerminalSession":
        if self._session.closed:
            self._session = aiohttp.ClientSession(cookie_jar=self.__cookie_jar)

        try:
            if not await self.check_login():
                await self._login()
        except Exception as e:
            logging.error(e)

        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()

    async def close(self):
        if not self._session.closed:
            await self._session.close()

    async def check_login(self):
        async with self._session.get(self.url) as resp:
            resp.raise_for_status()
            return str(resp.url) == self.url + "/Admin"

    async def _login(self):
        async with self._session.post(
            self.__login_url,
            data={"Login": self.__login, "Password": self.__password},
        ) as resp:
            resp.raise_for_status()
            if self.login_failed(resp):
                raise Exception("Login failed")

        logging.debug("Login successfull id=%s url=%s", self.terminal_id, self.url)

    def login_failed(self, response: aiohttp.ClientResponse):
        return str(response.url) == self.__login_url

    async def get_table_sales_page(self) -> str | None:
        async with self._session.get(self.__table_sales_url) as resp:
            resp.raise_for_status()
            logging.debug(
                "Getting table sales page successfull id=%s url=%s",
                self.terminal_id,
                self.url,
            )
            return await resp.text()

    async def add_bonuses_by_phone(
        self, phone: str, bonus_count: int, description: str
    ):
        id = await self.get_partner_id(phone)
        data = {
            "IdPartnerCore": f"{id}",
            "BonusCount": f"{bonus_count}",
            "Comment": description,
        }

        async with self._session.post(self.__bonus_create_url, data=data) as resp:
            resp.raise_for_status()

    async def get_partner_id(self, phone: str) -> int:
        if not is_phone_correct(phone):
            raise ValueError("Incorrect phone")

        phone = format_phone(phone_to_text(phone))
        url = self.get_partner_id_by_phone_url(phone)

        async with self._session.get(url) as resp:
            resp.raise_for_status()
            data: dict = await resp.json()
            partner_data = json.loads(data["Result"])

            if not partner_data:
                raise NoClientError("No partner with such phone")

            return partner_data[0]["Partner"]["Id"]

    def get_partner_id_by_phone_url(self, phone: str) -> str:
        phone = phone.replace("+", "%2B")
        return (
            self.url + f"/Modules/GetPartnersByPhoneContains?Phone={phone}"
            "&moduleName=%D0%91%D0%BE%D0%BD%D1%83%D1%81%D1%8B"
        )

    async def create_promo(self):
        """
        Function creates promocodes by sending request with next format
            data = {
                "Name": "",
                "DateStart": "",
                "DateEnd": "",
                "TypeCode": "",
                "Code": "",
                "StartCode": "",
                "EndCode": "",
                "CountCodeGen": "",
                "StartCodeGen": "",
                "EndCodeGen": "",
                "CountActivate": "1",
                "MaxDiscountAmount": "0",
                "OnlyNewPartners": "false",
                "ActivateType": "0",
                "Comment": "",
                "Phone": "",
                "PhoneComment": "",
                "IdGoodCore": "1",
                "TypeAction": "2",
                "Value": "0",
            }
        """
        data = {
            "Name": "TestForBot",
            "DateStart": "28.09.2023",
            "DateEnd": "28.10.2023",
            "TypeCode": "0",
            "Code": "1234567",
            "StartCode": "",
            "EndCode": "",
            "CountCodeGen": "",
            "StartCodeGen": "",
            "EndCodeGen": "",
            "CountActivate": "1",
            "MaxDiscountAmount": "0",
            "OnlyNewPartners": "false",
            "ActivateType": "0",
            "Comment": "1123",
            "Phone": "",
            "PhoneComment": "",
            "IdGoodCore": "1",
            "TypeAction": "2",
            "Value": "0",
        }
        async with self._session.post(
            self.url
            + "/Modules/ModulePartial_Post?ModuleUrl=http://localhost:8084&ActionUrl=Promocodes/Create",
            data=data,
        ) as resp:
            print(resp.raw_headers)


class NoClientError(Exception):
    ...
