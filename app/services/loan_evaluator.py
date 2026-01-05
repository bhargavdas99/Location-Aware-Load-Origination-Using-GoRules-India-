import logging
import httpx
from fastapi import HTTPException
from app.services.loan_workflow import LoanWorkflow
from app.services.zen_engine import LoanDecisionEngine
from app.repositories.loan_repository import LoanRepository
from app.repositories.rules_repository import RulesRepository
from app.services.external_services.external_services import ExternalServiceOrchestrator
from statemachine.exceptions import TransitionNotAllowed
from app.core.config import settings

# Configuration of logs
logger = logging.getLogger(__name__)


async def evaluate_loan(request, repo: LoanRepository, rules_repo: RulesRepository):
    # 1. RETRIEVAL: Find existing active loan or create new
    db_record = await repo.get_active_loan_by_pan(request.pan_number)
    if not db_record:
        db_record = await repo.create_loan(request.model_dump())

    # Initialize the External Service Orchestrator - this handles retries, timeouts, and actual HTTP calls
    external_services = ExternalServiceOrchestrator()

    # Initialize State Machine with the DB record
    sm = LoanWorkflow(db_record)

    # 2. ORCHESTRATION WITH ERROR HANDLING
    try:
        # --- Step: Identity Verification (API 1) ---
        if sm.current_state == sm.submitted:
            try:
                # Calls the External Service (pointing to /mock/identity)
                await external_services.check_identity(db_record.pan_number)
                sm.validate_api1()
                await repo.update_loan(db_record)
            except httpx.HTTPStatusError as e:
                # Catch 400 Bad Request (Regex failure in the mock)
                if e.response.status_code == 400:
                    raise HTTPException(
                        status_code=400, detail="Invalid PAN Card format."
                    )
                raise HTTPException(status_code=504, detail="Identity Service error.")
            except Exception as e:
                logger.error(f"Step API1 failed for loan {db_record.id}: {str(e)}")
                raise HTTPException(
                    status_code=504, detail="Identity Service unavailable."
                )

        # --- Step: Fraud Check (API 2) ---
        if sm.current_state == sm.api1_done:
            try:
                # Calls the External Service (pointing to /mock/fraud)
                await external_services.check_fraud(db_record.pan_number)
                sm.validate_api2()
                await repo.update_loan(db_record)
            except Exception as e:
                logger.error(
                    f"Step API2 failed after retries for loan {db_record.id}: {str(e)}"
                )
                raise HTTPException(
                    status_code=504, detail="Internal Fraud Check service timed out."
                )

        # --- Step: CIBIL Score Fetch (API 3) ---
        if sm.current_state == sm.api2_done:
            try:
                # Calls the External Service (pointing to /mock/cibil)
                response = await external_services.get_cibil_score(db_record.pan_number)
                db_record.bureau_score = response.get("score", 0)
                sm.fetch_cibil()
                await repo.update_loan(db_record)
            except Exception as e:
                logger.error(f"CIBIL fetch failed for loan {db_record.id}: {str(e)}")
                raise HTTPException(
                    status_code=504, detail="Credit Bureau service timed out."
                )

        # --- Step: GoRules Decision Engine ---
        if sm.current_state == sm.cibil_done:
            try:
                # Fetch JSON Rules from PostgreSQL (JSONB)
                rules_json = await rules_repo.get_rule_content(
                    settings.DECISION_RULE_KEY
                )
                if not rules_json:
                    logger.error(f"Decision failed: 'loan_decision' rule not found.")
                    raise Exception("Business rules not found in database.")

                engine = LoanDecisionEngine()
                input_data = {
                    **request.model_dump(),
                    "bureau_score": db_record.bureau_score,
                }

                # Evaluate against GoRules
                raw_result = engine.evaluate(rules_json, input_data)
                res = raw_result.get("result", {})

                # Update metadata fields from GoRules response
                db_record.approved_amount = float(res.get("approved_amount", 0.0))
                db_record.risk_assessment = res.get("risk_assessment")
                db_record.interest_rate = str(res.get("rate", "N/A"))
                db_record.decision_metadata = res

                if res.get("manual_review"):
                    sm.to_review()
                elif res.get("decision") == "APPROVED":
                    sm.to_approve()
                else:
                    sm.to_reject()

                # Persist the state change and metadata to Database
                await repo.update_loan(db_record)

            except Exception as e:
                logger.error(f"Rule Engine failed for loan {db_record.id}: {str(e)}")
                raise HTTPException(status_code=500, detail="Decision Engine Error.")

    except TransitionNotAllowed as e:
        logger.warning(f"Transition not allowed for loan {db_record.id}: {str(e)}")
        # Proceed to response mapping if already in a final state

    # 3. MAPPING RESPONSE
    metadata = db_record.decision_metadata or {}

    return {
        "loan_id": str(db_record.id),
        "status": db_record.status,
        "decision": metadata.get("decision"),
        "message": metadata.get("message"),
        "manual_review_required": db_record.status == "pending_review",
        "guarantor_required": metadata.get("guarantor_required", False),
        "credit_score": db_record.bureau_score or 0,
        "approved_amount": db_record.approved_amount or 0.0,
        "risk_assessment": db_record.risk_assessment or "N/A",
        "tier_applied": metadata.get("city_tier", request.city_tier),
        "max_eligible_amount": metadata.get("max_eligible", 0.0),
        "interest_rate": db_record.interest_rate or "N/A",
    }
