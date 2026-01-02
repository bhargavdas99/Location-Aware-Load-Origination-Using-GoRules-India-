from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.loan_model import LoanRecord


class LoanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_loan(self, loan_data: dict) -> LoanRecord:
        db_loan = LoanRecord(**loan_data)
        self.session.add(db_loan)
        await self.session.commit()
        await self.session.refresh(
            db_loan
        )  # this is to force python to get the latest version of the row.
        return db_loan

    async def update_loan(self, loan: LoanRecord):
        self.session.add(loan)
        await self.session.commit()
        await self.session.refresh(loan)
        return loan

    async def get_loan(self, loan_id: int) -> LoanRecord:
        result = await self.session.execute(
            select(LoanRecord).where(LoanRecord.id == loan_id)
        )
        return result.scalars().first()
