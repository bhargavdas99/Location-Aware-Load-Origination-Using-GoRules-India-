from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.risk_level import RiskLevelRule


class RiskLevelRuleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self):
        result = await self.session.execute(select(RiskLevelRule))
        return result.scalars().all()
