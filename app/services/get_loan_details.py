from app.repositories.loan_repository import LoanRepository


async def get_loan_details_action(loan_id: str, repo: LoanRepository):
    """
    Business logic for retrieving a single loan record.
    Returns the record if found, otherwise None.
    """
    return await repo.get_loan(loan_id)
