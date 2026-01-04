from app.repositories.loan_repository import LoanRepository
from app.services.loan_workflow import LoanWorkflow


async def approve_loan_manual_action(loan_id: str, repo: LoanRepository):
    """
    Orchestrates the manual approval transition using the state machine.
    """
    # get the loan record
    loan_record = await repo.get_loan(loan_id)
    if not loan_record:
        return None, "Loan Record Not Found"

    sm = LoanWorkflow(loan_record)

    try:
        sm.to_approve()
        await repo.update_loan(loan_record)
        return loan_record, None
    except Exception as e:
        return None, str(e)
