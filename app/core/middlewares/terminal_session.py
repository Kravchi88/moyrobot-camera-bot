from collections.abc import Awaitable, Callable
from typing import Any, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services.terminal.session import TerminalSession


class TerminalSesssionMiddleware(BaseMiddleware):
    def __init__(self, session: TerminalSession):
        self.session = session

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["terminal_session"] = self.session
        return await handler(event, data)
