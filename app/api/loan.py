from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.loan import LoanRequest, LoanResponse
from app.core.database import get_async_db
from app.services.credit.loan_evaluator import evaluate_loan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/loan", tags=["Loan"])


@router.post("/evaluate", response_model=LoanResponse)
async def evaluate(request: LoanRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Thin API layer: delegates all evaluation logic to the service.
    """
    try:
        return await evaluate_loan(request, db)
    except Exception as e:
        logger.error("Unexpected error in /loan/evaluate: %s", e)
        return LoanResponse(
            decision="ERROR",
            message="Internal server error.",
            manual_review_required=False,
            guarantor_required=False,
            credit_score=0,
            approved_amount=0,
            risk_assessment="UNKNOWN",
            tier_applied="UNKNOWN",
            max_eligible_amount=0,
            interest_rate="0.0",
        )
