from fastapi import APIRouter, HTTPException, Body
from app.services.external_services.api1_service import validate_identity
from app.services.external_services.api2_service import check_fraud_risk
from app.services.external_services.cibil_score_simulation import fetch_credit_score

router = APIRouter(prefix="/mock", tags=["Internal Mocks"])


@router.post("/identity")
async def mock_identity(payload: dict = Body(...)):
    result = await validate_identity(payload.get("pan", ""))
    if not result["valid"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/fraud")
async def mock_fraud():
    result = await check_fraud_risk()
    if not result["success"]:
        # 503 triggers the Tenacity retry in loan_evaluator
        raise HTTPException(status_code=503, detail=result["error"])
    return result


@router.post("/cibil")
async def mock_cibil(payload: dict = Body(...)):
    return await fetch_credit_score(payload.get("pan", ""))
