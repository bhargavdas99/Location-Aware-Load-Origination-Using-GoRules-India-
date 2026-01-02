import logging
from pathlib import Path
from app.services.loan_workflow import LoanWorkflow
from app.services.zen_engine import LoanDecisionEngine
from app.repositories.loan_repository import LoanRepository
from statemachine.exceptions import TransitionNotAllowed

logger = logging.getLogger(__name__)
RULES_FILE = Path(__file__).resolve().parent.parent / "rules" / "loan_decision.json"


async def evaluate_loan(request, repo: LoanRepository):
    # 1. Database Persistence Layer
    try:
        loan_data = request.model_dump()
        db_record = await repo.create_loan(loan_data)
    except Exception as e:
        logger.error(f"Database Error (Creation): {str(e)}")
        raise ValueError(f"Failed to initialize loan record: {str(e)}")

    # 2. Rules Engine Layer (GoRules)
    try:
        engine = LoanDecisionEngine()
        raw_result = engine.evaluate(str(RULES_FILE), loan_data)
        res = raw_result.get("result", {})
        if not res:
            raise ValueError("Decision engine returned an empty result.")
    except Exception as e:
        logger.error(f"Decision Engine Error: {str(e)}")
        raise ValueError(f"Error evaluating loan rules: {str(e)}")

    # 3. State Machine & Business Logic Layer
    try:
        sm = LoanWorkflow(db_record)
        decision = res.get("decision")
        manual_review = res.get("manual_review", False)

        # Handle the logic for REVIEW vs APPROVED vs REJECTED
        if decision == "APPROVED" and not manual_review:
            sm.to_approve()
        elif decision == "REVIEW" or manual_review is True:
            sm.to_review()
        else:
            sm.to_reject()

    except TransitionNotAllowed as e:
        logger.error(f"State Machine Error: Transition not allowed - {str(e)}")
        raise ValueError(f"Invalid workflow step: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected Workflow Error: {str(e)}")
        raise ValueError("Critical error during workflow transition.")

    # 4. Final Result Mapping & Update
    try:
        db_record.approved_amount = res.get("approved_amount", 0.0)
        db_record.risk_assessment = res.get("risk_assessment")
        db_record.interest_rate = res.get("rate")
        db_record.decision_metadata = res

        await repo.update_loan(db_record)

    except Exception as e:
        logger.error(f"Database Error (Update): {str(e)}")
        raise ValueError("Loan evaluated but failed to save final results.")

    return {
        "loan_id": db_record.id,
        "status": db_record.status,
        "decision": decision,
        "details": res,
    }
