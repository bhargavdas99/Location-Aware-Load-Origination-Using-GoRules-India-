from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.state_risk import StateRisk


class StateRiskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self):
        result = await self.session.execute(select(StateRisk))
        return result.scalars().all()
