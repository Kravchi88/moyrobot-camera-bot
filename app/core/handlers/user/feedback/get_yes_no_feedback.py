import logging
from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.handlers.user.feedback.utils import (
    get_feedback_id_from_state,
    send_feedback_to_reviewers,
)
from app.core.keyboards.menu import get_user_menu_reply_keyboard
from app.core.keyboards.yes_no import NO_BUTTON, YES_BUTTON, get_yes_no_reply_ketboard
from app.core.states.states import GetFeedback

from app.services.client_database.dao.feedback import FeedbackDAO
from app.services.client_database.dao.question import QuestionDAO
from app.services.client_database.models.feedback import Feedback
from app.services.client_database.models.question import Question
from app.services.client_database.models.user import User

logger = logging.getLogger(__name__)

get_yes_no_feedback_router = Router()


@get_yes_no_feedback_router.message(GetFeedback.get_yes_no_feedback, F.text)
async def msg_feedback(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    assert message.text is not None
    if message.text not in [YES_BUTTON, NO_BUTTON]:
        await message.answer(
            "Выберите ответ из клавиатуры!", reply_markup=get_yes_no_reply_ketboard()
        )
        return

    await message.answer(
        "Спасибо, что оставили отзыв!",
        reply_markup=await get_user_menu_reply_keyboard(message.chat.id, session),
    )
    feedback_id = await get_feedback_id_from_state(state)
    await state.clear()
    assert feedback_id is not None

    feedbackdao = FeedbackDAO(session)
    await feedbackdao.attach_message_by_ids(feedback_id, message.message_id)
    await send_feedback_to_reviewers(bot, feedback_id, session, send_yes_no_feedback)


async def send_yes_no_feedback(
    bot: Bot, user: User, feedback_id: int, session: AsyncSession
) -> Message:
    feedbackdao = FeedbackDAO(session)
    questiondao = QuestionDAO(session)
    feedback: Feedback = await feedbackdao.get_by_id(feedback_id)
    question: Question = await questiondao.get_by_id(feedback.question_id)
    messages: list = await feedbackdao.get_feedback_messages(feedback_id)
    text = (
        "Получен отзыв от клиента!\n"
        f"Вопрос: {question.text}\n"
        f"Ответ: {messages[0].text}"
    )

    return await bot.send_message(user.id, text)
