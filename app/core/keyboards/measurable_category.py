from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_measurable_category_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=f"{i} ⭐") for i in range(1, 6)]]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Оцените",
    )
