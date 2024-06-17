from datetime import datetime
from aiogram import F, Bot, Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.handlers.editor.upload_post import upload_post
from app.core.handlers.editor.utils import get_message_media_file_id
from app.core.keyboards.back import BackCB, get_back_keyboard

from app.core.keyboards.editor.create_post import (
    CreatePostCB,
    CreatePostTarget,
    SetUploadTimeCB,
    get_upload_time_keyboard,
    send_create_post_menu,
)
from app.core.keyboards.editor.post_part import send_edit_part_menu
from app.core.middlewares.create_post import CreatePostMiddleware, CreatePostStateData
from app.core.middlewares.media import MediaGroupMiddleware
from app.core.states.states import Editor
from app.services.client_database.dao.post import PostDAO
from app.services.client_database.models.post import Post, PostPartFile


create_post_router = Router()

create_post_router.message.middleware(CreatePostMiddleware())
create_post_router.callback_query.middleware(CreatePostMiddleware())
create_post_router.message.middleware(MediaGroupMiddleware())


@create_post_router.callback_query(
    Editor.CreatePost.menu, CreatePostCB.filter(F.target == CreatePostTarget.EDIT_PART)
)
async def cb_edit_part(
    cb: CallbackQuery,
    callback_data: CreatePostCB,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    session: AsyncSession,
):
    assert cb.message is not None
    await cb.answer()
    await create_post_state_data.set_selected_part_number(callback_data.part_number)
    await send_edit_part_menu(cb.message, state, create_post_state_data, session)


@create_post_router.callback_query(
    Editor.CreatePost.menu, CreatePostCB.filter(F.target == CreatePostTarget.ADD_PART)
)
async def cb_add_part(
    cb: CallbackQuery,
    state: FSMContext,
):
    assert cb.message is not None
    await cb.answer()
    await state.set_state(Editor.CreatePost.get_part)
    await cb.message.edit_text(
        "Пришлите сообщения для поста, можете прикрепить до 10 фото/видео",
        reply_markup=get_back_keyboard(),
    )


@create_post_router.message(Editor.CreatePost.get_part, F.media_group_id)
async def add_part_with_media(
    message: Message,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
    album: list[Message],
):
    text = message.caption
    if text is None:
        await message.answer("Укажите текст", reply_markup=get_back_keyboard())
        return

    album = sorted(album, key=lambda x: x.message_id)
    media = [get_message_media_file_id(message) for message in album]
    await create_post_state_data.add_post_part(text, media)

    await send_create_post_menu(message.answer, state, create_post_state_data)


@create_post_router.message(Editor.CreatePost.get_part, or_f(F.photo, F.video))
async def add_part_with_photo_or_video(
    message: Message,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
):
    caption = message.caption
    if caption is None:
        await message.answer("Укажите текст", reply_markup=get_back_keyboard())
        return

    media = [get_message_media_file_id(message)]
    await create_post_state_data.add_post_part(caption, media)

    await send_create_post_menu(message.answer, state, create_post_state_data)


@create_post_router.message(Editor.CreatePost.get_part, F.text)
async def add_part_with_text(
    message: Message,
    state: FSMContext,
    create_post_state_data: CreatePostStateData,
):
    assert message.text is not None
    await create_post_state_data.add_post_part(message.text)
    await send_create_post_menu(message.answer, state, create_post_state_data)


@create_post_router.callback_query(
    Editor.CreatePost.menu,
    CreatePostCB.filter(F.target == CreatePostTarget.DELETE_POST),
)
async def cb_delete_post(
    cb: CallbackQuery,
    create_post_state_data: CreatePostStateData,
    state: FSMContext,
):
    assert cb.message is not None
    await cb.answer()
    await create_post_state_data.delete_post()
    await create_post_state_data._init()
    await send_create_post_menu(cb.message.edit_text, state, create_post_state_data)


@create_post_router.callback_query(
    Editor.CreatePost.menu,
    CreatePostCB.filter(F.target == CreatePostTarget.SET_UPLOAD_TIME),
)
async def cb_set_upload_time(
    cb: CallbackQuery,
    state: FSMContext,
):
    assert cb.message is not None
    await cb.answer()
    await state.set_state(Editor.CreatePost.get_upload_time)
    await cb.message.edit_text(
        "Введите дату и время когда нужно выложить пост\n" "Пример: 30.11.23 16:40:20",
        reply_markup=get_upload_time_keyboard(),
    )


@create_post_router.callback_query(
    Editor.CreatePost.get_upload_time, SetUploadTimeCB.filter()
)
async def cb_upload_time_after(
    cb: CallbackQuery,
    create_post_state_data: CreatePostStateData,
    state: FSMContext,
):
    assert cb.message is not None
    await cb.answer()
    await create_post_state_data.set_upload_time(None)
    await send_create_post_menu(cb.message.edit_text, state, create_post_state_data)


@create_post_router.message(Editor.CreatePost.get_upload_time, F.text)
async def get_upload_time(
    message: Message,
    create_post_state_data: CreatePostStateData,
    state: FSMContext,
):
    assert message.text is not None

    try:
        time = datetime.strptime(message.text, "%d.%m.%y %H:%M:%S")
    except Exception as e:
        print(e)
        await message.answer("Неверный формат", reply_markup=get_back_keyboard())
        return

    await create_post_state_data.set_upload_time(time)
    await send_create_post_menu(message.answer, state, create_post_state_data)


@create_post_router.callback_query(
    Editor.CreatePost.menu,
    CreatePostCB.filter(F.target == CreatePostTarget.UPLOAD_POST),
)
async def cb_upload_post(
    cb: CallbackQuery,
    create_post_state_data: CreatePostStateData,
    state: FSMContext,
    session: AsyncSession,
    scheduler: AsyncIOScheduler,
    bot: Bot,
):
    assert cb.message is not None
    await cb.answer()
    upload_time = await create_post_state_data.get_upload_time()

    if upload_time is not None and upload_time < datetime.now():
        await cb.answer("Время отпарвки поста меньше текущего", show_alert=True)
        return

    postdao = PostDAO(session)

    post_upload_time = upload_time if upload_time else datetime.now()
    post = await postdao.add(Post(upload_date=post_upload_time))

    post_parts = await create_post_state_data.get_post_parts()
    for part in post_parts:
        part.post_id = post.id
        await postdao.add(part)
        medias = await create_post_state_data.get_post_part_media(part.part_number)
        for i, media in enumerate(medias):
            await postdao.add(
                PostPartFile(
                    post_id=post.id,
                    part_number=part.part_number,
                    file_order=i,
                    file_id=media,
                )
            )

    if upload_time is None:
        await upload_post(bot, post.id, session)
    else:
        scheduler.add_job(
            upload_post,
            trigger="date",
            run_date=upload_time,
            args=(bot, post.id, session),
            name=f"Uploading post with id {post.id}",
        )

    await state.clear()
    await cb.message.delete()


@create_post_router.callback_query(
    Editor.CreatePost.menu,
    BackCB.filter(),
)
async def cb_back(
    cb: CallbackQuery,
    state: FSMContext,
):
    assert cb.message is not None
    await cb.answer()
    await state.set_state()
    await cb.message.delete()


@create_post_router.callback_query(
    or_f(Editor.CreatePost.get_part, Editor.CreatePost.get_upload_time),
    BackCB.filter(),
)
async def cb_back_from_inner(
    cb: CallbackQuery,
    create_post_state_data: CreatePostStateData,
    state: FSMContext,
):
    assert cb.message is not None
    await send_create_post_menu(cb.message.edit_text, state, create_post_state_data)
