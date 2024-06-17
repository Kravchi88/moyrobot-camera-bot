from aiogram import F, Bot, Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.handlers.editor.utils import get_message_media_file_id
from app.core.keyboards.back import BackCB, get_back_keyboard
from app.core.keyboards.editor.create_post import send_create_post_menu
from app.core.keyboards.editor.post_part import (
    EditPostPartCB,
    EditPostPartTarget,
    get_change_media_keyboard,
    send_edit_part_menu,
)
from app.core.middlewares.create_post import CreatePostMiddleware, CreatePostStateData
from app.core.middlewares.media import MediaGroupMiddleware

from app.core.states.states import Editor


edit_part_router = Router()
edit_part_router.message.middleware(CreatePostMiddleware())
edit_part_router.message.middleware(MediaGroupMiddleware())
edit_part_router.callback_query.middleware(CreatePostMiddleware())


@edit_part_router.callback_query(
    Editor.CreatePost.EditPart.menu,
    EditPostPartCB.filter(F.target == EditPostPartTarget.CHANGE_MEDIA),
)
async def cb_change_media(
    cb: CallbackQuery,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    bot: Bot,
):
    assert cb.message is not None
    await cb.answer()
    await state.set_state(Editor.CreatePost.EditPart.change_media)
    await delete_media_messages(cb.message.chat.id, create_post_state_data, bot)
    await cb.message.edit_text(
        "Пришлите новые фото/видео или удалите уже существующие",
        reply_markup=get_change_media_keyboard(),
    )


@edit_part_router.callback_query(
    Editor.CreatePost.EditPart.change_media,
    EditPostPartCB.filter(F.target == EditPostPartTarget.DELETE_MEDIA),
)
async def cb_delete_media(
    cb: CallbackQuery,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    session: AsyncSession,
):
    assert cb.message is not None
    await cb.answer()
    await create_post_state_data.update_selected_post_part(media=[])
    await send_edit_part_menu(cb.message, state, create_post_state_data, session)


@edit_part_router.message(Editor.CreatePost.EditPart.change_media, F.media_group_id)
async def add_part_with_media(
    message: Message,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    album: list[Message],
    session: AsyncSession,
):
    album = sorted(album, key=lambda x: x.message_id)
    media = [get_message_media_file_id(message) for message in album]
    await create_post_state_data.update_selected_post_part(media=media)
    await send_edit_part_menu(
        message, state, create_post_state_data, session, delete_message=False
    )


@edit_part_router.message(
    Editor.CreatePost.EditPart.change_media, or_f(F.photo, F.video)
)
async def add_part_with_photo_or_video(
    message: Message,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    session: AsyncSession,
):
    media = [get_message_media_file_id(message)]
    await create_post_state_data.update_selected_post_part(media=media)
    await send_edit_part_menu(
        message, state, create_post_state_data, session, delete_message=False
    )


@edit_part_router.callback_query(
    Editor.CreatePost.EditPart.menu,
    EditPostPartCB.filter(F.target == EditPostPartTarget.CHANGE_TEXT),
)
async def cb_change_text(
    cb: CallbackQuery,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    bot: Bot,
):
    assert cb.message is not None
    await cb.answer()
    await state.set_state(Editor.CreatePost.EditPart.change_text)
    await delete_media_messages(cb.message.chat.id, create_post_state_data, bot)
    await cb.message.edit_text("Введите новый текст", reply_markup=get_back_keyboard())


@edit_part_router.message(Editor.CreatePost.EditPart.change_text, F.text)
async def change_text(
    message: Message,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    session: AsyncSession,
):
    await create_post_state_data.update_selected_post_part(text=message.text)
    await send_edit_part_menu(
        message, state, create_post_state_data, session, delete_message=False
    )


@edit_part_router.callback_query(
    Editor.CreatePost.EditPart.menu,
    EditPostPartCB.filter(F.target == EditPostPartTarget.DELETE),
)
async def cb_delete(
    cb: CallbackQuery,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    bot: Bot,
):
    assert cb.message is not None
    await cb.answer()
    await create_post_state_data.delete_selected_post_part()
    await delete_media_messages(cb.message.chat.id, create_post_state_data, bot)
    await send_create_post_menu(cb.message.edit_text, state, create_post_state_data)


@edit_part_router.callback_query(
    or_f(
        Editor.CreatePost.EditPart.change_text, Editor.CreatePost.EditPart.change_media
    ),
    BackCB.filter(),
)
async def cb_change_text_back(
    cb: CallbackQuery,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    session: AsyncSession,
):
    assert cb.message is not None
    await cb.answer()
    await send_edit_part_menu(cb.message, state, create_post_state_data, session)


@edit_part_router.callback_query(Editor.CreatePost.EditPart.menu, BackCB.filter())
async def cb_back(
    cb: CallbackQuery,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    bot: Bot,
):
    assert cb.message is not None
    await cb.answer()
    await delete_media_messages(cb.message.chat.id, create_post_state_data, bot)
    await send_create_post_menu(cb.message.edit_text, state, create_post_state_data)


async def delete_media_messages(
    chat_id: int, create_post_state_data: CreatePostStateData, bot: Bot
):
    messages = await create_post_state_data.get_media_messges()
    for message in messages:
        await bot.delete_message(chat_id, message)


async def delete_bot_message(
    chat_id: int, create_post_state_data: CreatePostStateData, bot: Bot
):
    message_id = await create_post_state_data.get_bot_message_id()
    await bot.delete_message(chat_id, message_id)
