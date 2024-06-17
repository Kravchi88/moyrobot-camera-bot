from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.core.keyboards.back import get_back_inline_button
from app.core.middlewares.create_post import CreatePostStateData
from app.core.states.states import Editor
from app.services.client_database.models.post import PostPart


class CreatePostTarget(IntEnum):
    EDIT_PART = auto()
    ADD_PART = auto()
    DELETE_POST = auto()
    SET_UPLOAD_TIME = auto()
    UPLOAD_POST = auto()


class CreatePostCB(CallbackData, prefix="create_post"):
    target: CreatePostTarget
    part_number: int


def get_create_post_keyboard(post_parts: list[PostPart]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for part in post_parts:
        builder.row(
            InlineKeyboardButton(
                text=f"{part.text[:10]}...",
                callback_data=CreatePostCB(
                    target=CreatePostTarget.EDIT_PART, part_number=part.part_number
                ).pack(),
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="Добавить часть поста",
            callback_data=CreatePostCB(
                target=CreatePostTarget.ADD_PART, part_number=-1
            ).pack(),
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="Удалить пост",
            callback_data=CreatePostCB(
                target=CreatePostTarget.DELETE_POST, part_number=-1
            ).pack(),
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="Установить время поста",
            callback_data=CreatePostCB(
                target=CreatePostTarget.SET_UPLOAD_TIME, part_number=-1
            ).pack(),
        ),
    )

    builder.row(
        get_back_inline_button(),
        InlineKeyboardButton(
            text="Выложить пост",
            callback_data=CreatePostCB(
                target=CreatePostTarget.UPLOAD_POST, part_number=-1
            ).pack(),
        ),
    )
    return builder.as_markup()


async def send_create_post_menu(
    func,
    state: FSMContext,
    create_post_data: CreatePostStateData,
):
    await state.set_state(Editor.CreatePost.menu)
    post_parts = await create_post_data.get_post_parts()
    upload_time = await create_post_data.get_upload_time()
    if upload_time is None:
        upload_time = "Сразу"
    else:
        upload_time = upload_time.strftime("%d.%m.%y %H:%M:%S")
    await func(
        f"Создать пост\nВремя: {upload_time}",
        reply_markup=get_create_post_keyboard(post_parts),
    )


class SetUploadTimeCB(CallbackData, prefix="upload_time"):
    ...


def get_upload_time_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        get_back_inline_button(),
        InlineKeyboardButton(text="Сразу", callback_data=SetUploadTimeCB().pack()),
    )
    return builder.as_markup()
