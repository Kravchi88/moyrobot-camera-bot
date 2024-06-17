from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from app.services.cameras.camera_stream import CameraStream


class CamerasStreamsMiddleware(BaseMiddleware):
    def __init__(self, streams: list[CameraStream]):
        super().__init__()
        self.streams = streams

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["streams"] = self.streams
        return await handler(event, data)
