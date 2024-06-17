from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class NextPostPartCB(CallbackData, prefix="part_number"):
    post_id: int
    part_number: int


def get_next_post_part_keyboard(
    post_id: int, current_part_number: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Далее",
            callback_data=NextPostPartCB(
                post_id=post_id, part_number=current_part_number + 1
            ).pack(),
        )
    )
    return builder.as_markup()
