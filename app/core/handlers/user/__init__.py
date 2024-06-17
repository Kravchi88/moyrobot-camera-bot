from aiogram import Router
from app.core.handlers.user.feedback import feedback_router

user_router = Router()
user_router.include_routers(feedback_router)
