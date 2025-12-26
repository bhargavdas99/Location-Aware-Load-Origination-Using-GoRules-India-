from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from app.schemas.loan import LoanRequest, LoanResponse
from app.core.database import get_db
from app.services.credit.loan_evaluator import evaluate_loan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/loan", tags=["Loan"])


@router.post("/evaluate", response_model=LoanResponse)
def evaluate(request: LoanRequest, db: Session = Depends(get_db)):
    """
    Thin API layer: delegates all evaluation logic to the service.
    """
    return evaluate_loan(request, db)
