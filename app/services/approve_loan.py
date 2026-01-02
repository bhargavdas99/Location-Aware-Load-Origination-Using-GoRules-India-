from app.repositories.loan_repository import LoanRepository
from app.services.loan_workflow import LoanWorkflow
from sqlalchemy.ext.asyncio import AsyncSession


async def approve_loan_manual_action(
    loan_id: str, db: AsyncSession, repo: LoanRepository
):
    """
    Orchestrates the manual approval transition using the state machine.
    """
    # 1. DATABASE TRANSACTION: Start here
    async with db.begin():
        loan_record = await repo.get_loan(loan_id)
        if not loan_record:
            return None, "Not Found"

        # Pass repo to workflow so it can save history
        sm = LoanWorkflow(loan_record)

        try:
            sm.to_approve()
            # SQLAlchemy handles the version_id update automatically here
            return loan_record, None
        except Exception as e:
            return None, str(e)
