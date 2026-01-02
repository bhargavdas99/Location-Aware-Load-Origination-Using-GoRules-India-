from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.schemas.loan import LoanRequest
from app.repositories.loan_repository import LoanRepository
from app.services.loan_evaluator import evaluate_loan
import traceback
from app.services.get_loan_details import get_loan_details_action
from app.services.approve_loan import approve_loan_manual_action

router = APIRouter(prefix="/loan", tags=["Loan"])


@router.post("/evaluate")
async def evaluate(request: LoanRequest, db: AsyncSession = Depends(get_async_db)):
    try:
        repo = LoanRepository(db)
        return await evaluate_loan(request, repo)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/loan-status/{loan_id}")
async def get_loan_status(loan_id: str, db: AsyncSession = Depends(get_async_db)):
    repo = LoanRepository(db)
    loan = await get_loan_details_action(loan_id, repo)

    if not loan:
        raise HTTPException(status_code=404, detail="Loan record not found")

    return {
        "id": loan.id,
        "status": loan.status,
        "approved_amount": loan.approved_amount,
        "risk": loan.risk_assessment,
        "full_metadata": loan.decision_metadata,
    }


@router.post("/approve-manual/{loan_id}")
async def approve_manual(loan_id: str, db: AsyncSession = Depends(get_async_db)):
    repo = LoanRepository(db)

    updated_loan, error = await approve_loan_manual_action(loan_id, db, repo)

    if error == "Loan not found":
        raise HTTPException(status_code=404, detail=error)
    if error:
        raise HTTPException(status_code=400, detail=f"Workflow Error: {error}")

    return {
        "loan_id": updated_loan.id,
        "message": "Loan manually approved by manager",
        "new_status": updated_loan.status,
    }
