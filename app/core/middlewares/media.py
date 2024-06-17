import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Union

from aiogram import BaseMiddleware
from aiogram.enums import InputMediaType
from aiogram.types import (
    Message,
    TelegramObject,
)

from app.services.client_database import models

DEFAULT_DELAY = 0.6


class MediaGroupMiddleware(BaseMiddleware):
    ALBUM_DATA: Dict[str, List[Message]] = {}

    def __init__(self, delay: Union[int, float] = DEFAULT_DELAY):
        self.delay = delay

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        try:
            self.ALBUM_DATA[event.media_group_id].append(event)
            return  # Don't propagate the event
        except KeyError:
            self.ALBUM_DATA[event.media_group_id] = [event]
            await asyncio.sleep(self.delay)
            data["album"] = self.ALBUM_DATA.pop(event.media_group_id)

        return await handler(event, data)


def create_file_model(message: Message) -> models.File:
    if message.photo:
        return models.File(
            message.photo[-1].file_id, InputMediaType.PHOTO, message.caption
        )
    elif message.video:
        return models.File(message.video.file_id, InputMediaType.VIDEO, message.caption)

    raise ValueError("Can't create other file types")
