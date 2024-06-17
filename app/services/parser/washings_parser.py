import asyncio
from datetime import datetime
import io
import re
import pandas as pd
from typing import Optional


from app.services.client_database.models.washing import Washing

from app.services.terminal.session import TerminalSession
from app.utils.phone import phone_to_text


class WashingsParser:
    def __init__(self, sessions: list[TerminalSession]) -> None:
        self.sessions: list[TerminalSession] = sessions

    async def get_washings(self) -> list[Washing]:
        tasks = self.create_getting_tasks()
        return [wash for washings in await asyncio.gather(*tasks) for wash in washings]

    def create_getting_tasks(self) -> list[asyncio.Task]:
        return [
            asyncio.create_task(self._get_washings(session))
            for session in self.sessions
        ]

    async def _get_washings(self, terminal_session: TerminalSession) -> list[Washing]:
        washings_page = await self.get_washings_page(terminal_session)

        if washings_page is None or washings_page == "":
            return []

        return self.parse_washings_page(terminal_session.terminal_id, washings_page)

    async def get_washings_page(
        self, terminal_session: TerminalSession
    ) -> Optional[str]:
        async with terminal_session as session:
            return await session.get_table_sales_page()

    def parse_washings_page(self, terminal_id: int, page: str) -> list[Washing]:
        df = self.get_washings_dataframe(page)
        return self.parse_washings_dataframe(terminal_id, df)

    def get_washings_dataframe(self, page: str) -> pd.DataFrame:
        df = pd.read_html(io.StringIO(page))[0]
        return df

    def parse_washings_dataframe(
        self, terminal_id: int, df: pd.DataFrame
    ) -> list[Washing]:
        return [
            self.create_washing(terminal_id, washing)
            for washing in df[df["Тип запуска  БУМ"] == "Автоматический"].iloc
        ]

    def create_washing(self, terminal_id: int, washing_row: pd.Series) -> Washing:
        id = str(washing_row["Id"])
        terminal = terminal_id
        date = self.get_date(washing_row["Дата"])
        state = washing_row["Состояние  БУМ"]
        start_date = self.get_date(washing_row["Дата запуска  БУМ"])
        end_date = self.get_date(washing_row["Дата завершения  БУМ"])
        mode = self.get_mode(washing_row["Режим  БУМ"])
        phone = self.get_phone(washing_row["Клиент"])
        bonuses = self.get_bonuses(washing_row["Бонусы  Бонусы"])
        promocode = self.get_promocode(washing_row["Промокод  Промокоды"])
        price = int(washing_row["Сумма"]) // 100

        return Washing(
            id=id,
            terminal=terminal,
            date=date,
            state=state,
            start_date=start_date,
            end_date=end_date,
            mode=mode,
            phone=phone,
            bonuses=bonuses,
            promocode=promocode,
            price=price,
        )

    def get_date(self, date) -> Optional[datetime]:
        if pd.isna(date) or date == "Не определено":
            return None
        return datetime.strptime(str(date), "%d.%m.%Y %H:%M:%S")

    def get_mode(self, mode) -> int:
        return int(mode.split()[1])

    def get_phone(self, phone) -> Optional[str]:
        if pd.isna(phone):
            return None
        return phone_to_text(phone)

    def get_bonuses(self, bonuses) -> Optional[int]:
        if pd.isna(bonuses):
            return None
        return int(bonuses)

    def get_promocode(self, promocode) -> Optional[int]:
        if pd.isna(promocode):
            return None
        promocode = re.findall(r"[0-9]+", promocode)
        return int(promocode[0])
