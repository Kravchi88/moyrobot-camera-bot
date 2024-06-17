from enum import IntEnum, auto
from typing import List
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.keyboards.back import get_back_inline_button
from app.core.middlewares.create_post import CreatePostStateData
from app.core.states.states import Editor
from app.services.client_database.dao.file import FileDAO


class EditPostPartTarget(IntEnum):
    CHANGE_MEDIA = auto()
    DELETE_MEDIA = auto()
    CHANGE_TEXT = auto()
    DELETE = auto()


class EditPostPartCB(CallbackData, prefix="edit_post_part"):
    target: EditPostPartTarget


def get_edit_post_part_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Изменить прикреплённое медиа",
            callback_data=EditPostPartCB(target=EditPostPartTarget.CHANGE_MEDIA).pack(),
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="Изменить текст",
            callback_data=EditPostPartCB(target=EditPostPartTarget.CHANGE_TEXT).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Удалить",
            callback_data=EditPostPartCB(target=EditPostPartTarget.DELETE).pack(),
        )
    )

    builder.row(get_back_inline_button())
    return builder.as_markup()


async def send_edit_part_menu(
    message: Message,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    session: AsyncSession,
    delete_message=True,
):
    if delete_message:
        await message.delete()

    await state.set_state(Editor.CreatePost.EditPart.menu)
    media = await get_post_part_media(create_post_state_data, session)
    if media:
        media_messages = await message.answer_media_group(media=media)
    else:
        part = await create_post_state_data.get_selected_post_part()
        media_messages = [await message.answer(part.text)]

    await create_post_state_data.set_media_messges(
        [message.message_id for message in media_messages]
    )
    await message.answer(
        "Выберите действие", reply_markup=get_edit_post_part_keyboard()
    )


async def get_post_part_media(
    create_post_state_data: CreatePostStateData, session: AsyncSession
) -> List[InputMediaPhoto | InputMediaVideo | InputMediaDocument | InputMediaAudio]:
    part_number = await create_post_state_data.get_selected_part_number()
    post_part = await create_post_state_data.get_post_part(part_number)
    attached_files_id = await create_post_state_data.get_post_part_media(part_number)

    filedao = FileDAO(session)
    attached_files = [await filedao.get_by_id(id) for id in attached_files_id]

    builder = MediaGroupBuilder(caption=post_part.text)
    for file in attached_files:
        builder.add(type=file.type, media=file.id)  # type: ignore

    return builder.build()


def get_change_media_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        get_back_inline_button(),
        InlineKeyboardButton(
            text="Удалить",
            callback_data=EditPostPartCB(target=EditPostPartTarget.DELETE_MEDIA).pack(),
        ),
    )
    return builder.as_markup()
