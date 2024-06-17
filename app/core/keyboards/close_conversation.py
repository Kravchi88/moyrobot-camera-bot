from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


CLOSE_CONVERSATION_BUTTON_TEXT = "Прекратить беседу с клиентом"


def get_close_conversation_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=CLOSE_CONVERSATION_BUTTON_TEXT),
            ],
        ],
        resize_keyboard=True,
    )
