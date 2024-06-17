from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.client_database.dao.user import UserDAO
from app.services.client_database.dao.washing import WashingDAO
from app.services.client_database.models.user import User
from app.services.client_database.models.washing import Washing
from app.services.scheduler.washings_handling.client_feedback import (
    create_storage_key,
    send_feedback_request,
)
from app.settings.config import Config


tests_router = Router()


@tests_router.message(Command(commands=["test_feedback"]))
async def test_feedback(
    message: Message,
    bot: Bot,
    command: CommandObject,
    state: FSMContext,
    session: AsyncSession,
    config: Config,
):
    userdao = UserDAO(session)
    washingdao = WashingDAO(session)

    user: User | None = await userdao.get_by_id(message.chat.id)
    if user is None:
        await message.answer("Произошла ошибка при получении пользователя")
        return

    washing: Washing | None = await washingdao.get_by_id("263063")
    if washing is None:
        await message.answer("Произошла ошибка при получении мойки")
        return

    key = create_storage_key(bot, user)
    new_state = FSMContext(storage=state.storage, key=key)
    await send_feedback_request(bot, user, washing, config, new_state)
