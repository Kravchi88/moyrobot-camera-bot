from datetime import datetime
from aiogram.enums import InputMediaType
from aiogram.types import Message

from app.services.client_database import models


def create_message_model(
    message: Message,
) -> models.Message:
    if message.from_user is None:
        raise ValueError("No from_user field in message")
    text = ""
    if message.text:
        text = message.text
    elif message.caption:
        text = message.caption

    user_message = models.Message(
        id=message.message_id,
        user_id=message.from_user.id,
        date=datetime.now(),
        text=text,
    )
    return user_message


def get_message_attached_file(message: Message) -> models.File | None:
    if message.text:
        return None

    file = models.File()
    file.caption = message.caption or ""

    if message.photo:
        file.id = message.photo[-1].file_id
        file.type = InputMediaType.PHOTO
    elif message.video:
        file.id = message.video.file_id
        file.type = InputMediaType.VIDEO
    elif message.animation:
        file.id = message.animation.file_id
        file.type = InputMediaType.ANIMATION
    elif message.audio:
        file.id = message.audio.file_id
        file.type = InputMediaType.AUDIO
    elif message.document:
        file.id = message.document.file_id
        file.type = InputMediaType.DOCUMENT

    if file.id is None or file.type is None:
        raise ValueError("No id and type was specified for attached file")
    return file
