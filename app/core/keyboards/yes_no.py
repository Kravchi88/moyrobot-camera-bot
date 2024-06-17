from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class YesNoChoice(IntEnum):
    YES = auto()
    NO = auto()


class YesNoCB(CallbackData, prefix="yes_no"):
    choice: YesNoChoice


YES_BUTTON = "Да"
NO_BUTTON = "Нет"


def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=NO_BUTTON, callback_data=YesNoCB(choice=YesNoChoice.NO).pack()
        ),
        InlineKeyboardButton(
            text=YES_BUTTON, callback_data=YesNoCB(choice=YesNoChoice.YES).pack()
        ),
    )

    return builder.as_markup()


def get_yes_no_reply_ketboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=NO_BUTTON),
                KeyboardButton(text=YES_BUTTON),
            ],
        ],
        resize_keyboard=True,
    )
