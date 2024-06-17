from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any, Dict, Optional
from typing_extensions import override
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject
from app.core.middlewares.state_data import StateData
from app.services.client_database.models.post import PostPart


class CreatePostStateData(StateData):
    @classmethod
    async def create(cls, state: FSMContext) -> "CreatePostStateData":
        return await super().create(state, "create_post")

    @override
    def _get_init_state_data(self) -> dict[str, Any]:
        return {
            "upload_time": None,
            "post_parts": [],
            "media_messages": [],
        }

    async def delete_post(self):
        await self._set_data(None)

    async def set_upload_time(self, time: datetime | None):
        if time is None:
            await self._update_data(upload_time=None)
            return

        await self._update_data(upload_time=time.strftime("%d.%m.%y %H:%M:%S"))

    async def get_upload_time(self) -> datetime | None:
        time = await self._get_data_key_value("upload_time")
        if time is None:
            return None

        return datetime.strptime(time, "%d.%m.%y %H:%M:%S")

    async def set_bot_message_id(self, message_id: int):
        await self._update_data(bot_message_id=message_id)

    async def get_bot_message_id(self) -> int:
        return await self._get_data_key_value("bot_message_id")

    async def set_selected_part_number(self, part_number: int):
        await self._update_data(selected_part_number=part_number)

    async def get_selected_part_number(self) -> int:
        return await self._get_data_key_value("selected_part_number")

    async def set_media_messges(self, messages: list[int]):
        await self._update_data(media_messages=messages)

    async def get_media_messges(self) -> list[int]:
        return await self._get_data_key_value("media_messages")

    async def delete_media_messages(self):
        await self._update_data(media_messages=[])

    async def _set_post_parts_data(self, data: list[dict[str, Any]]):
        await self._update_data(post_parts=data)

    async def _get_post_parts_data(self) -> list[dict[str, Any]]:
        return await self._get_data_key_value("post_parts")

    async def get_post_parts(self) -> list[PostPart]:
        data = await self._get_post_parts_data()
        return [PostPart(part_number=i, text=val["text"]) for i, val in enumerate(data)]

    async def update_post_part(
        self,
        part_number: int,
        text: Optional[str] = None,
        media_messages: Optional[list[str]] = None,
    ):
        post_part = await self._get_post_part_data(part_number)
        if text is not None:
            post_part["text"] = text
        if media_messages is not None:
            post_part["media"] = media_messages

        await self._update_post_part_data(part_number, post_part)

    async def _update_post_part_data(self, part_number: int, data: dict[str, Any]):
        post_parts = await self._get_post_parts_data()
        post_parts[part_number] = data
        await self._set_post_parts_data(post_parts)

    async def _get_post_part_data(self, part_number: int) -> dict[str, Any]:
        post_parts = await self._get_post_parts_data()
        return post_parts[part_number]

    async def get_post_part(self, part_number: int) -> PostPart:
        post_parts = await self.get_post_parts()
        return post_parts[part_number]

    async def add_post_part(self, text: str, media: Optional[list[str]] = None):
        if text is None:
            text = ""

        if media is None:
            media = []

        post_parts = await self._get_post_parts_data()
        post_parts.append({"text": text, "media": media})
        await self._set_post_parts_data(post_parts)

    async def delete_post_part(self, part_number: int):
        post_parts = await self._get_post_parts_data()
        post_parts.pop(part_number)
        await self._set_post_parts_data(post_parts)

    async def get_post_part_media(self, part_number: int) -> list[int]:
        part = await self._get_post_part_data(part_number)
        return part["media"]

    async def get_selected_post_part(self) -> PostPart:
        selected_part_number = await self.get_selected_part_number()
        return await self.get_post_part(selected_part_number)

    async def update_selected_post_part(
        self, text: Optional[str] = None, media: Optional[list[str]] = None
    ):
        selected_part_number = await self.get_selected_part_number()
        await self.update_post_part(selected_part_number, text, media)

    async def delete_selected_post_part(self):
        selected_part_number = await self.get_selected_part_number()
        await self.delete_post_part(selected_part_number)


class CreatePostMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        create_post_state_data = await CreatePostStateData.create(data["state"])
        data["create_post_state_data"] = create_post_state_data
        return await handler(event, data)
