from aiogram import F, Bot, Router
from aiogram.types import ContentType, Message
from aiogram.utils.media_group import MediaGroupBuilder
from app.core.middlewares.feedback_conversation import (
    FeedbackConversationMiddleware,
    FeedbackConversationStateData,
)
from app.core.middlewares.media import MediaGroupMiddleware
from app.core.states.states import Client


feedback_conversation_router = Router()
feedback_conversation_router.message.middleware(FeedbackConversationMiddleware())
feedback_conversation_router.message.middleware(MediaGroupMiddleware())


@feedback_conversation_router.message(Client.feedback_conversation, F.media_group_id)
async def msg_album_feedback(
    message: Message,
    album: list[Message],
    feedback_conversation: FeedbackConversationStateData,
    bot: Bot,
):
    """This handler will receive a complete album of any type."""

    reviewer_id = await feedback_conversation.get_reviewer_id()
    caption = message.caption or ""
    mediabuilder = MediaGroupBuilder(caption=caption)
    for mes in album:
        match mes.content_type:
            case ContentType.PHOTO:
                mediabuilder.add_photo(media=mes.photo[-1].file_id)  # type: ignore
            case ContentType.VIDEO:
                mediabuilder.add_video(media=mes.video.file_id)  # type: ignore
    await bot.send_media_group(reviewer_id, media=mediabuilder.build())


@feedback_conversation_router.message(Client.feedback_conversation, F.text)
async def feedback_conversation_text(
    message: Message,
    feedback_conversation: FeedbackConversationStateData,
    bot: Bot,
):
    assert message.text is not None

    reviewer_id = await feedback_conversation.get_reviewer_id()
    await bot.send_message(reviewer_id, text=message.text)


@feedback_conversation_router.message(Client.feedback_conversation, F.photo)
async def feedback_conversation_photo(
    message: Message,
    feedback_conversation: FeedbackConversationStateData,
    bot: Bot,
):
    assert message.photo is not None

    reviewer_id = await feedback_conversation.get_reviewer_id()
    await bot.send_photo(
        reviewer_id, photo=message.photo[-1].file_id, caption=message.caption
    )


@feedback_conversation_router.message(Client.feedback_conversation, F.video)
async def feedback_conversation_video(
    message: Message,
    feedback_conversation: FeedbackConversationStateData,
    bot: Bot,
):
    assert message.video is not None

    reviewer_id = await feedback_conversation.get_reviewer_id()
    await bot.send_video(
        reviewer_id, video=message.video.file_id, caption=message.caption
    )
