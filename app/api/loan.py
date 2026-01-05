from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.schemas.loan import LoanRequest
from app.repositories.loan_repository import LoanRepository
from app.repositories.rules_repository import RulesRepository
from app.services.loan_evaluator import evaluate_loan
import traceback

router = APIRouter(prefix="/loan", tags=["Loan"])


@router.post("/evaluate")
async def evaluate(request: LoanRequest, db: AsyncSession = Depends(get_async_db)):
    try:
        repo = LoanRepository(db)
        rules_repo = RulesRepository(db)
        return await evaluate_loan(request, repo, rules_repo)
    except HTTPException as http_exc:
        # Re-raise the specific error we intended (400, 504, etc.)
        raise http_exc
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
