from enum import IntEnum, auto
from aiogram.fsm.context import FSMContext


class MailingType(IntEnum):
    TEXT = auto()
    PHOTO = auto()


async def get_mailing_type(state: FSMContext) -> MailingType:
    data = await state.get_data()
    mailing_type = data.get("mailing_type")

    if not isinstance(mailing_type, int):
        raise TypeError("state_mailing_type is not MailingType")
    return MailingType(mailing_type)
