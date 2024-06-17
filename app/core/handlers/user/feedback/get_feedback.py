from aiogram import F, Bot, Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
)
from aiogram.utils.media_group import MediaGroupBuilder
from apscheduler.executors.base import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.handlers.user.feedback.utils import (
    get_feedback_id_from_state,
    send_feedback_to_reviewers,
    send_text_feedback,
)
from app.core.keyboards.answer_feedback import get_answer_feedback_keyboard
from app.core.keyboards.menu import get_user_menu_reply_keyboard
from app.core.middlewares.media import MediaGroupMiddleware

from app.core.states.states import GetFeedback
from app.services.client_database.dao.feedback import FeedbackDAO
from app.services.client_database.dao.question import QuestionDAO
from app.services.client_database.dao.user import UserDAO
from app.services.client_database.models.feedback import Feedback
from app.services.client_database.models.question import Question
from app.services.client_database.models.role import PermissionEnum
from app.services.client_database.models.user import User

logger = logging.getLogger(__name__)

get_feedback_router = Router()
get_feedback_router.message.filter(GetFeedback.get_feedback)
get_feedback_router.message.middleware(MediaGroupMiddleware())


@get_feedback_router.message(F.text)
async def msg_feedback(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    await message.answer(
        "Спасибо, что оставили отзыв!",
        reply_markup=await get_user_menu_reply_keyboard(message.chat.id, session),
    )
    feedback_id = await get_feedback_id_from_state(state)
    await state.clear()
    assert feedback_id is not None

    feedbackdao = FeedbackDAO(session)
    await feedbackdao.attach_message_by_ids(feedback_id, message.message_id)
    await send_feedback_to_reviewers(bot, feedback_id, session, send_text_feedback)


@get_feedback_router.message(or_f(F.video, F.photo))
async def msg_with_attachment_feedback(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    await message.answer(
        "Спасибо, что оставили отзыв!",
        reply_markup=await get_user_menu_reply_keyboard(message.chat.id, session),
    )
    feedback_id = await get_feedback_id_from_state(state)
    await state.clear()
    assert feedback_id is not None

    feedbackdao = FeedbackDAO(session)
    await feedbackdao.attach_message_by_ids(feedback_id, message.message_id)
    await send_feedback_to_reviewers(
        bot, feedback_id, session, send_feedback_with_attached_files
    )


@get_feedback_router.message(F.media_group_id)
async def msg_album_feedback(
    message: Message,
    album: list[Message],
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
):
    """This handler will receive a complete album of any type."""
    await message.answer(
        "Спасибо, что оставили отзыв!",
        reply_markup=await get_user_menu_reply_keyboard(message.chat.id, session),
    )
    feedback_id = await get_feedback_id_from_state(state)
    await state.clear()
    assert feedback_id is not None

    feedbackdao = FeedbackDAO(session)
    for mes in album:
        await feedbackdao.attach_message_by_ids(feedback_id, mes.message_id)

    await send_feedback_to_reviewers(
        bot, feedback_id, session, send_feedback_with_attached_files
    )


async def send_feedback_with_attached_files(
    bot: Bot, user: User, feedback_id: int, session: AsyncSession
) -> Message:
    feedbackdao = FeedbackDAO(session)
    questiondao = QuestionDAO(session)
    userdao = UserDAO(session)
    feedback: Feedback = await feedbackdao.get_by_id(feedback_id)
    question: Question = await questiondao.get_by_id(feedback.question_id)
    attached_files = await feedbackdao.get_attached_files_to_feedback(feedback_id)
    text = "Получен отзыв от клиента!\n" f"Вопрос: {question.text}\n" "Ответ: "

    reply_markup = None
    if await userdao.is_user_have_permission(user.id, PermissionEnum.ANSWER_FEEDBACK):
        reply_markup = get_answer_feedback_keyboard(feedback.id)

    caption = attached_files[0].caption or ""
    mediabuilder = MediaGroupBuilder(caption=text + caption)
    for file in attached_files:
        mediabuilder.add(type=file.type, media=file.id, caption=file.caption)  # type: ignore

    await bot.send_media_group(user.id, media=mediabuilder.build())
    return await bot.send_message(
        user.id, "Ответить на отзыв", reply_markup=reply_markup
    )
