from collections.abc import Awaitable, Callable
from enum import StrEnum
from typing import Any, Dict, Optional
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject


class FeedbackConversationStateData:
    class Keys(StrEnum):
        FEEDBACK_ID = "feedback_id"
        CLIENT_ID = "client_id"
        REVIEWER_ID = "reviewer_id"

    def __init__(self, state: FSMContext):
        self.state = state

    async def init(
        self,
        feedback_id: Optional[int] = None,
        client_id: Optional[int] = None,
        reviewer_id: Optional[int] = None,
    ):
        data = {
            self.Keys.FEEDBACK_ID: feedback_id,
            self.Keys.CLIENT_ID: client_id,
            self.Keys.REVIEWER_ID: reviewer_id,
        }
        await self.set_feedback_convesation_data(data)

    async def get_feedback_conversation_data(self) -> dict:
        data = await self.state.get_data()
        return data["feedback_conversation"]

    async def set_feedback_convesation_data(self, data: dict) -> None:
        await self.state.update_data(feedback_conversation=data)

    async def update_feedback_conversation_data(self, **kwargs):
        data = await self.get_feedback_conversation_data()
        data.update(**kwargs)
        await self.set_feedback_convesation_data(data)

    async def get_feedback_conversation_data_key_value(self, key: Any) -> Any:
        data = await self.get_feedback_conversation_data()
        return data[key]

    async def get_feedback_id(self) -> int:
        return await self.get_feedback_conversation_data_key_value(
            self.Keys.FEEDBACK_ID
        )

    async def get_client_id(self) -> int:
        return await self.get_feedback_conversation_data_key_value(self.Keys.CLIENT_ID)

    async def get_reviewer_id(self) -> int:
        return await self.get_feedback_conversation_data_key_value(
            self.Keys.REVIEWER_ID
        )


class FeedbackConversationMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        ...

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["feedback_conversation"] = FeedbackConversationStateData(data["state"])
        return await handler(event, data)
