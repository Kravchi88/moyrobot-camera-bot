from collections.abc import Awaitable, Callable
from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.types.message import Message
from apscheduler.executors.base import logging
from apscheduler.schedulers.asyncio import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.keyboards.answer_feedback import get_answer_feedback_keyboard
from app.services.client_database.dao.feedback import FeedbackDAO
from app.services.client_database.dao.question import QuestionDAO
from app.services.client_database.dao.user import UserDAO

from app.services.client_database.models.feedback import Feedback
from app.services.client_database.models.question import Question
from app.services.client_database.models.role import PermissionEnum
from app.services.client_database.models.user import User

SEND_FEEDBACK_DELAY = 0.05

SendFeedbackFunction = Callable[
    [Bot, User, int, AsyncSession], Awaitable[types.Message]
]


async def get_feedback_dict_from_state(state: FSMContext) -> dict | None:
    data = await state.get_data()
    return data.get("feedback")


async def get_feedback_id_from_state(state: FSMContext) -> int | None:
    feedback = await get_feedback_dict_from_state(state)
    if feedback is None:
        return None
    return feedback.get("id")


async def get_feedback_from_state(
    state: FSMContext, session: AsyncSession
) -> Feedback | None:
    feedback_id: int | None = await get_feedback_id_from_state(state)

    feedbackdao = FeedbackDAO(session)
    if feedback_id is None:
        return None
    return await feedbackdao.get_by_id(feedback_id)


async def send_feedback_to_reviewers(
    bot: Bot, feedback_id: int, session: AsyncSession, send_func: SendFeedbackFunction
):
    userdao = UserDAO(session)
    feedbackdao = FeedbackDAO(session)
    reviewers = await userdao.get_users_by_permission(PermissionEnum.GET_FEEDBACK)

    for user in reviewers:
        try:
            message = await send_func(bot, user, feedback_id, session)
            await feedbackdao.add_feedback_notification(
                feedback_id, user.id, message.message_id
            )
        except Exception as e:
            logging.error(e)

        await asyncio.sleep(SEND_FEEDBACK_DELAY)


async def send_text_feedback(
    bot: Bot, user: User, feedback_id: int, session: AsyncSession
) -> Message:
    feedbackdao = FeedbackDAO(session)
    questiondao = QuestionDAO(session)
    userdao = UserDAO(session)
    feedback: Feedback = await feedbackdao.get_by_id(feedback_id)
    question: Question = await questiondao.get_by_id(feedback.question_id)
    messages: list = await feedbackdao.get_feedback_messages(feedback_id)
    text = (
        "Получен отзыв от клиента!\n"
        f"Вопрос: {question.text}\n"
        f"Ответ: {messages[0].text}"
    )

    reply_markup = None
    if await userdao.is_user_have_permission(user.id, PermissionEnum.ANSWER_FEEDBACK):
        reply_markup = get_answer_feedback_keyboard(feedback.id)

    return await bot.send_message(user.id, text, reply_markup=reply_markup)
