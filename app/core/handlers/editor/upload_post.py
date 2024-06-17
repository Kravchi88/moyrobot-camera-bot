import asyncio
import logging
from typing import List
from aiogram import Bot, Router
from aiogram.types import (
    CallbackQuery,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.keyboards.post import NextPostPartCB, get_next_post_part_keyboard
from app.services.client_database.dao.post import PostDAO

from app.services.client_database.dao.user import UserDAO


SEND_DELAY = 0.6


upload_post_router = Router()


@upload_post_router.callback_query(NextPostPartCB.filter())
async def next_post_part(
    cb: CallbackQuery, callback_data: NextPostPartCB, session: AsyncSession, bot: Bot
):
    assert cb.message is not None
    await cb.answer()

    parts_count = len(await PostDAO(session).get_post_parts(callback_data.post_id))
    await send_post_part(
        bot,
        cb.message.chat.id,
        callback_data.post_id,
        callback_data.part_number,
        session,
        parts_count,
    )


async def upload_post(bot: Bot, post_id: int, session: AsyncSession):
    userdao = UserDAO(session)
    users = await userdao.get_all()
    for user in users:
        try:
            await send_post(bot, user.id, post_id, session)
        except Exception as e:
            logging.error(e)
        await asyncio.sleep(SEND_DELAY)


async def send_post(bot: Bot, chat_id: int, post_id: int, session: AsyncSession):
    parts_count = len(await PostDAO(session).get_post_parts(post_id))
    PARTS_START_INDEX = 0
    await send_post_part(bot, chat_id, post_id, PARTS_START_INDEX, session, parts_count)


async def send_post_part(
    bot: Bot,
    chat_id: int,
    post_id: int,
    part_number: int,
    session: AsyncSession,
    parts_count: int,
):
    postdao = PostDAO(session)
    media = await get_post_part_media(post_id, part_number, session)
    if media:
        await bot.send_media_group(chat_id, media=media)
    else:
        post_part = await postdao.get_post_part(post_id, part_number)
        await bot.send_message(chat_id, post_part.text)

    if part_number == parts_count - 1:
        return

    await bot.send_message(
        chat_id,
        text="Нажмите чтобы посмотреть следующую часть",
        reply_markup=get_next_post_part_keyboard(post_id, part_number),
    )


async def get_post_part_media(
    post_id: int, part_number: int, session: AsyncSession
) -> List[InputMediaPhoto | InputMediaVideo | InputMediaDocument | InputMediaAudio]:
    postdao = PostDAO(session)
    post_part = await postdao.get_post_part(post_id, part_number)
    attached_files = await postdao.get_post_part_attached_files(post_id, part_number)

    builder = MediaGroupBuilder(caption=post_part.text)
    for file in attached_files:
        builder.add(type=file.type, media=file.id)  # type: ignore

    return builder.build()
