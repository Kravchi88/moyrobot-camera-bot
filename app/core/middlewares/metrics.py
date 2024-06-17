from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any

from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.services.client_database.dao.message import MessageDAO
from app.utils.message import create_message_model, get_message_attached_file


class MessageModelMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker) -> None:
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any],
    ) -> Any:
        message_model = create_message_model(message)

        attached_file = get_message_attached_file(message)
        async with self.session_pool() as session:
            messagedao = MessageDAO(session)
            await messagedao.add(message_model)
            if attached_file is not None:
                await messagedao.attach_file(message_model, attached_file)

        return await handler(message, data)
