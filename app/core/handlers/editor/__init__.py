from aiogram import Router
from app.core.handlers.editor.create_post import create_post_router
from app.core.handlers.editor.edit_part import edit_part_router
from app.core.handlers.editor.upload_post import upload_post_router

editor_router = Router()
editor_router.include_routers(create_post_router, edit_part_router, upload_post_router)
