from sqlalchemy.ext.asyncio import AsyncSession
from app.services.client_database.dao.client_bonus import ClientBonusDAO
from app.services.client_database.models.client_bonus import ClientBonus
from app.services.client_database.models.washing import Washing


async def update_bonuses(washings: list[Washing], session: AsyncSession):
    clientbonusdao = ClientBonusDAO(session)
    for washing in washings:
        if await clientbonusdao.get_by_phone(washing.phone) is None:
            await clientbonusdao.add(
                ClientBonus(
                    phone=washing.phone,
                )
            )

        await clientbonusdao.add_bonuses(washing.phone, washing.bonuses)
