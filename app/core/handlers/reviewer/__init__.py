from aiogram import Router
from app.core.handlers.reviewer.feedback_conversation import (
    feedback_conversation_router,
)


reviewer_router = Router()
reviewer_router.include_routers(feedback_conversation_router)
