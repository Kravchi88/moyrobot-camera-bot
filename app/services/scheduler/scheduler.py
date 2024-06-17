from aiogram import Bot
from aiogram.fsm.storage.base import BaseStorage
from sqlalchemy.ext.asyncio import async_sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.scheduler.washings_handling.setup import setup_handle_washings_job
from app.services.terminal.session import TerminalSession


def setup_scheduler(
    scheduler: AsyncIOScheduler,
    bot: Bot,
    terminal_sessions: list[TerminalSession],
    sessionmaker: async_sessionmaker,
    state_storage: BaseStorage,
) -> AsyncIOScheduler:
    setup_handle_washings_job(
        scheduler, bot, terminal_sessions, sessionmaker, state_storage
    )
    return scheduler
