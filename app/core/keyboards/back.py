from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup


BACK_BUTTON_TEXT = "Назад"


class BackCB(CallbackData, prefix="back"):
    ...


def get_back_inline_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data=BackCB().pack())


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [get_back_inline_button()],
        ],
    )
