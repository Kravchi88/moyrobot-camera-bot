from aiogram import Router
from app.core.handlers.user.feedback.get_feedback import get_feedback_router
from app.core.handlers.user.feedback.get_measurable_feedback import (
    get_measurable_feedback_router,
)


from app.core.handlers.user.feedback.get_yes_no_feedback import (
    get_yes_no_feedback_router,
)
from app.core.handlers.user.feedback.conversation import feedback_conversation_router

feedback_router = Router()

feedback_router.include_routers(
    get_feedback_router,
    get_yes_no_feedback_router,
    get_measurable_feedback_router,
    feedback_conversation_router,
)
