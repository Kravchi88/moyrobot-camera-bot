from aiogram.types import Message


def get_message_media_file_id(message: Message) -> str:
    if message.photo:
        return message.photo[-1].file_id
    elif message.video:
        return message.video.file_id
    return ""
