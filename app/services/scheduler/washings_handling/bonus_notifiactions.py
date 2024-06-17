from aiogram import Bot
from apscheduler.executors.base import logging
from apscheduler.schedulers.asyncio import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.client_database.dao.client_bonus import ClientBonusDAO
from app.services.client_database.dao.user import UserDAO
from app.services.client_database.models.client_bonus import ClientBonus
from app.services.client_database.models.user import User

from app.services.client_database.models.washing import Washing


SEND_NOTIFICATION_DELAY = 0.06


async def send_bonus_notifications(
    bot: Bot, washings: list[Washing], session: AsyncSession
):
    userdao = UserDAO(session)
    clientbonusdao = ClientBonusDAO(session)
    for washing in washings:
        users: list[User] = await userdao.get_users_by_phone(washing.phone)
        bonus_balance: ClientBonus = await clientbonusdao.get_by_phone(washing.phone)

        if bonus_balance is None:
            continue
        if washing.bonuses is None:
            continue

        if washing.bonuses > 0:
            text = (
                "Начисление бонусов за мойку!\n"
                f"Количество: {washing.bonuses}\n"
                f"Текущий баланс: {bonus_balance.actual_amount}\n"
            )
        else:
            text = (
                "Списание бонусов!\n"
                f"Количество: {washing.bonuses}\n"
                f"Текущий баланс: {bonus_balance.actual_amount}\n"
            )

        for user in users:
            try:
                await bot.send_message(user.id, text=text)
            except Exception as e:
                logging.error(e)

            await asyncio.sleep(SEND_NOTIFICATION_DELAY)
