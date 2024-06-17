from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from apscheduler.executors.base import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.handlers.user.feedback.utils import (
    get_feedback_id_from_state,
    send_feedback_to_reviewers,
)
import re
from app.core.keyboards.answer_feedback import get_answer_feedback_keyboard
from app.core.keyboards.measurable_category import get_measurable_category_keyboard
from app.core.keyboards.menu import get_user_menu_reply_keyboard

from app.core.states.states import GetFeedback
from app.services.client_database.dao.feedback import FeedbackDAO
from app.services.client_database.dao.message import MessageDAO
from app.services.client_database.dao.question import QuestionDAO
from app.services.client_database.dao.user import UserDAO
from app.services.client_database.models.feedback import Feedback
from app.services.client_database.models.question import CategoryEnum, Question
from app.services.client_database.models.role import PermissionEnum
from app.services.client_database.models.user import User
from app.services.terminal.session import TerminalSession

logger = logging.getLogger(__name__)

get_measurable_feedback_router = Router()
get_measurable_feedback_router.message.filter(GetFeedback.get_measurable_feedback)

pattern = re.compile(r"[1-5] ⭐", re.UNICODE)


@get_measurable_feedback_router.message(F.text)
async def msg_measurable_feedback(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
    terminal_session: TerminalSession,
):
    """This handler will receive a complete album of any type."""
    assert message.text is not None
    if not pattern.match(message.text):
        await message.answer(
            "Выберите рейтинг из клавиатуры!",
            reply_markup=get_measurable_category_keyboard(),
        )
        return

    await message.answer(
        "Спасибо, что оставили отзыв!",
        reply_markup=await get_user_menu_reply_keyboard(message.chat.id, session),
    )
    feedback_id = await get_feedback_id_from_state(state)
    await state.clear()

    mark = message.text.split()[0]
    assert feedback_id is not None

    feedbackdao = FeedbackDAO(session)
    messagedao = MessageDAO(session)
    await feedbackdao.attach_message_by_ids(feedback_id, message.message_id)
    await messagedao.change_message(message.message_id, mark)
    await send_feedback_to_reviewers(
        bot, feedback_id, session, send_measurable_feedback
    )

    if (
        await feedbackdao.is_feedback_question_have_category(
            feedback_id, CategoryEnum.WASHING
        )
        and int(mark) <= 3
    ):
        await send_bonuses_for_bad_serivce(
            message, feedback_id, terminal_session, session
        )


async def send_measurable_feedback(
    bot: Bot, user: User, feedback_id: int, session: AsyncSession
) -> Message:
    feedbackdao = FeedbackDAO(session)
    questiondao = QuestionDAO(session)
    userdao = UserDAO(session)
    feedback: Feedback = await feedbackdao.get_by_id(feedback_id)
    question: Question = await questiondao.get_by_id(feedback.question_id)
    messages: list = await feedbackdao.get_feedback_messages(feedback_id)
    mark = int(messages[0].text)
    mark_text = "⭐" * mark
    text = (
        "Получен отзыв от клиента!\n" f"Вопрос: {question.text}\n" f"Ответ: {mark_text}"
    )
    reply_markup = None
    if await userdao.is_user_have_permission(user.id, PermissionEnum.ANSWER_FEEDBACK):
        reply_markup = get_answer_feedback_keyboard(feedback.id)

    return await bot.send_message(user.id, text, reply_markup=reply_markup)


async def send_bonuses_for_bad_serivce(
    message: Message,
    feedback_id: int,
    terminal_session: TerminalSession,
    session: AsyncSession,
):
    client_id = message.chat.id
    if await is_client_already_sent_before_bad_feedback(
        client_id, feedback_id, CategoryEnum.WASHING, session
    ):
        return

    userdao = UserDAO(session)
    user: User = await userdao.get_by_id(client_id)

    await message.answer(
        "Очень жаль, что вы так оценили наши услуги(\nВ качестве извенения мы начислим вам 100 бонусов"
    )

    async with terminal_session as term_session:
        await term_session.add_bonuses_by_phone(user.phone, 100, "За плохой отзыв")


async def is_client_already_sent_before_bad_feedback(
    client_id: int, feedback_id: int, category: CategoryEnum, session: AsyncSession
):
    feedbackdao = FeedbackDAO(session)
    feedbacks = await feedbackdao.get_client_feedbacks(client_id, category)
    for feedback in feedbacks:
        if feedback.id == feedback_id:
            continue
        messages: list = await feedbackdao.get_feedback_messages(feedback.id)
        mark = messages[0].text
        if int(mark) <= 3:
            return True
    return False
