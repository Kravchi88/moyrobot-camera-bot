from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


stats_router = Router()


@stats_router.message(Command(commands=["stats"]))
async def cmd_stats(message: Message, session: AsyncSession):
    """
    Send table from view daily_usage

    """
    query = text("SELECT * FROM daily_usage LIMIT 12;")
    result = await session.execute(query)
    message_text = ""
    for row in result:
        message_text += f"{row[0]}\t{row[1]}\n"
    await message.answer(message_text)
