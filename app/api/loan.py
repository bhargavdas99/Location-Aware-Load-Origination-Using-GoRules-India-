from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.loan import LoanRequest, LoanResponse
from app.core.database import get_async_db
from app.services.credit.loan_evaluator import evaluate_loan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/loan", tags=["Loan"])


@router.post("/evaluate", response_model=LoanResponse)
async def evaluate(request: LoanRequest, db: AsyncSession = Depends(get_async_db)):
    try:
        return await evaluate_loan(request, db)
    except Exception as e:
        logger.error("Unexpected error in /loan/evaluate: %s", e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while evaluating the loan.",
        )
