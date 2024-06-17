from aiogram import Bot
from aiogram.fsm.storage.base import BaseStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.parser.washings_parser import WashingsParser
from app.services.scheduler.washings_handling.bonus_notifiactions import (
    send_bonus_notifications,
)
from app.services.scheduler.washings_handling.client_feedback import (
    create_send_feedback_request_jobs,
)
from app.services.scheduler.washings_handling.update_bonuses import update_bonuses
from app.services.scheduler.washings_handling.update_washings import update_washings
from app.services.scheduler.washings_handling.utils import (
    filter_new_washings_with_bonuses,
)

from app.services.terminal.session import TerminalSession


def setup_handle_washings_job(
    scheduler: AsyncIOScheduler,
    bot: Bot,
    terminal_sessions: list[TerminalSession],
    session: async_sessionmaker,
    state_storage: BaseStorage,
):
    scheduler.add_job(
        func=do_parser_work,
        trigger="cron",
        minute="*/1",
        args=(bot, terminal_sessions, session, scheduler, state_storage),
        name="Update database job",
    )


async def do_parser_work(
    bot: Bot,
    terminal_sessions: list[TerminalSession],
    sessionmaker: async_sessionmaker,
    scheduler: AsyncIOScheduler,
    state_storage: BaseStorage,
):
    parser = WashingsParser(terminal_sessions)
    washings = await parser.get_washings()
    async with sessionmaker() as session:
        new_washings = await filter_new_washings_with_bonuses(washings, session)
        await update_bonuses(new_washings, session)
        await send_bonus_notifications(bot, new_washings, session)
        await create_send_feedback_request_jobs(
            scheduler, bot, new_washings, session, state_storage
        )

        await update_washings(washings, session)
