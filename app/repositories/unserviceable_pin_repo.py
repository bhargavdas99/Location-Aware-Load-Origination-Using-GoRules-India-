from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.unserviceable_pin import UnserviceablePin


class UnserviceablePinRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self):
        result = await self.session.execute(select(UnserviceablePin))
        return result.scalars().all()
