from sqlalchemy.ext.asyncio import AsyncSession
from app.services.client_database.dao.washing import WashingDAO
from app.services.client_database.models.washing import Washing


async def update_washings(washings: list[Washing], session: AsyncSession):
    washingdao = WashingDAO(session)
    for washing in washings:
        await washingdao.add(washing)
