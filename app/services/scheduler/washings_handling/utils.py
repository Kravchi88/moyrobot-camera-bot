from sqlalchemy.ext.asyncio import AsyncSession
from app.services.client_database.dao.washing import WashingDAO
from app.services.client_database.models.washing import Washing


async def filter_new_washings_with_bonuses(
    washings: list[Washing], session: AsyncSession
) -> list[Washing]:
    return [
        washing
        for washing in await filter_new_washings(washings, session)
        if washing.phone is not None and washing.bonuses is not None
    ]


async def filter_new_washings(
    washings: list[Washing], session: AsyncSession
) -> list[Washing]:
    washingdao = WashingDAO(session)
    return [
        washing
        for washing in washings
        if not await washingdao.is_washing_exists(washing)
    ]
