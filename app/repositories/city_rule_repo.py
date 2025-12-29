from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.city_rules import CityRule


class CityRuleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self):
        result = await self.session.execute(select(CityRule))
        return result.scalars().all()
