from typing import Optional
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.client_database.dao.user import UserDAO
from app.services.client_database.models.role import PermissionEnum
from app.services.client_database.models.user import User

from app.utils.phone import format_phone


SEE_QUEUE_BUTTON_TEXT = "Посмотреть очередь 👀"
GET_BONUSES_BUTTON_TEXT = "Узнать бонусы 💰"
PHONE_BUTTON_TEXT = "Телефон📱: "
CREATE_POST_BUTTON_TEXT = "Сделать пост 📝"


def get_menu_reply_keyboard(
    permissions: list[str],
    phone: Optional[str] = None,
) -> ReplyKeyboardMarkup:
    phone_text = "Не указан"
    if phone is not None:
        phone_text = format_phone(phone)

    keyboard = [
        [
            KeyboardButton(text=SEE_QUEUE_BUTTON_TEXT),
            KeyboardButton(text=GET_BONUSES_BUTTON_TEXT),
        ],
        [
            KeyboardButton(text=PHONE_BUTTON_TEXT + f"{phone_text}"),
        ],
    ]

    if PermissionEnum.CREATE_POST in permissions:
        keyboard.append([KeyboardButton(text=CREATE_POST_BUTTON_TEXT)])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
    )


async def get_user_menu_reply_keyboard(
    user_id: int, session: AsyncSession
) -> ReplyKeyboardMarkup:
    userdao = UserDAO(session=session)
    user: User = await userdao.get_by_id(user_id)
    permissions = [p.name for p in await userdao.get_user_permissions(user_id)]
    return get_menu_reply_keyboard(permissions, user.phone)
