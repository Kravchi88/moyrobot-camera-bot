from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton


ENTER_TEXT = "Готово"


class EnterCB(CallbackData, prefix="enter"):
    ...


def get_enter_inline_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=ENTER_TEXT, callback_data=EnterCB().pack())
