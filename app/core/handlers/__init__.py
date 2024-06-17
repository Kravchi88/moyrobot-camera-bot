from aiogram import Router
from app.core.handlers.main import router as main_router
from app.core.handlers.user import user_router
from app.core.handlers.admin import admin_router
from app.core.handlers.reviewer import reviewer_router
from app.core.handlers.editor import editor_router


handlers_router = Router()
handlers_router.include_routers(
    main_router,
    editor_router,
    user_router,
    admin_router,
    reviewer_router,
)
