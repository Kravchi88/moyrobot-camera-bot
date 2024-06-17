import logging
from typing_extensions import assert_never
from aiogram import Bot, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.keyboards.cancel import CancelCB, get_cancel_keyboard
from app.core.keyboards.yes_no import YesNoCB, YesNoChoice, get_yes_no_keyboard
from app.core.states.states import SendPromo
from app.core.utils.send_promo import get_mailing_type, MailingType

from app.services.client_database.dao.user import UserDAO

promo_router = Router()


SENDING_PROMO_DELAY = 0.04  # 40 milliseconds


@promo_router.message(Command(commands=["promo"]))
async def cmb_promo(
    message: Message,
    state: FSMContext,
):
    """
    Handler for starting dialog for send promo functional
    """
    await state.set_state(SendPromo.text_promo_message)
    await message.answer(
        "Введите текст сообщения для рассылки", reply_markup=get_cancel_keyboard()
    )


@promo_router.callback_query(SendPromo.text_promo_message, CancelCB.filter())
async def cancel_text_promo(cb: CallbackQuery, state: FSMContext):
    """
    Handling user press cancel button
    """
    await cb.answer()
    await state.clear()
    await cb.message.delete()  # pyright: ignore


@promo_router.message(SendPromo.text_promo_message, F.text)
async def get_promo_text(message: Message, state: FSMContext):
    """
    Handling getting promo text
    """
    html_text = message.html_text

    await state.set_state(SendPromo.send_promo_message)
    await state.update_data(mailing_type=MailingType.TEXT)
    await state.update_data(html_mailing=html_text)

    await message.answer(html_text, parse_mode=ParseMode.HTML)
    await message.answer(
        "Вы хотите начать рассылку?",
        parse_mode=ParseMode.HTML,
        reply_markup=get_yes_no_keyboard(),
    )


@promo_router.message(SendPromo.text_promo_message, F.photo)
async def get_promo_photo(message: Message, state: FSMContext):
    """
    Handling getting promo with caption
    """
    html_text = message.html_text
    photo = message.photo[-1]  # pyright: ignore

    await state.set_state(SendPromo.send_promo_message)
    await state.update_data(mailing_type=MailingType.PHOTO)
    await state.update_data(html_mailing=html_text)
    await state.update_data(mailing_photo_id=photo.file_id)

    await message.answer_photo(photo=photo.file_id, caption=html_text)
    await message.answer(
        "Вы хотите начать рассылку?",
        parse_mode=ParseMode.HTML,
        reply_markup=get_yes_no_keyboard(),
    )


@promo_router.callback_query(
    SendPromo.send_promo_message, YesNoCB.filter(F.choice == YesNoChoice.YES)
)
async def yes_promo_send(
    cb: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession
):
    """
    Hadling start mailing
    """
    await cb.answer()
    await cb.message.edit_reply_markup()  # pyright: ignore

    try:
        await start_mailing(bot, state, session)
    except Exception:
        await cb.message.answer("Не удалось произвести рассылку(")  # type: ignore
        return

    await cb.message.edit_text(text="Рассылка произведена!")  # pyright: ignore


async def start_mailing(bot: Bot, state: FSMContext, session: AsyncSession):
    match await get_mailing_type(state):
        case MailingType.TEXT:
            await start_text_mailing(bot, session, state)
        case MailingType.PHOTO:
            await start_photo_mailing(bot, session, state)
        case _ as never:
            assert_never(never)


async def start_text_mailing(bot: Bot, session: AsyncSession, state: FSMContext):
    userdao = UserDAO(session=session)
    users = await userdao.get_all()
    data = await state.get_data()
    html_text = data.get("html_mailing")

    if html_text is None:
        raise ValueError("Mailing Message is None")

    for user in users:
        try:
            await bot.send_message(user.id, text=html_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.debug(e)
            continue


async def start_photo_mailing(bot: Bot, session: AsyncSession, state: FSMContext):
    userdao = UserDAO(session=session)
    users = await userdao.get_all()
    data = await state.get_data()
    html_text = data.get("html_mailing")
    mailing_photo_id = data.get("mailing_photo_id")

    if html_text is None:
        raise ValueError("Mailing Message is None")
    if mailing_photo_id is None:
        raise ValueError("Mailing Photo is None")

    for user in users:
        try:
            await bot.send_photo(
                user.id,
                photo=mailing_photo_id,
                caption=html_text,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logging.debug(e)

        await asyncio.sleep(SENDING_PROMO_DELAY)


@promo_router.callback_query(
    SendPromo.send_promo_message, YesNoCB.filter(F.choice == YesNoChoice.NO)
)
async def no_promo_send(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Рассылка отменена!")  # pyright: ignore
