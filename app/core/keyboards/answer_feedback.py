from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class AnswerFeedbackCB(CallbackData, prefix="answer_feedback"):
    feedback_id: int


def get_answer_feedback_keyboard(feedback_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Ответить на отзыв",
        callback_data=AnswerFeedbackCB(feedback_id=feedback_id).pack(),
    )

    return builder.as_markup()
