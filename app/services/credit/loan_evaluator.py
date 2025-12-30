from pathlib import Path
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.credit import (
    calculate_credit_score,
    get_risk_level,
)
from app.services.credit.loaders import (
    load_bureau_config_from_json,
    load_rules,
    load_stability_config,
)
from app.services.los_post_actions import (
    notify_applicant,
    create_loan_record,
    generate_repayment_schedule,
)
from app.services.zen_engine import LoanDecisionEngine

logger = logging.getLogger(__name__)
decision_engine = LoanDecisionEngine()

RULES_FILE = (
    Path(__file__).resolve().parent.parent.parent / "rules" / "loan_decision.json"
)


async def evaluate_loan(request, db: AsyncSession):
    """
    Evaluates loan request. If critical steps fail, exceptions bubble up to the Router.
    """
    # 1. Load Data (If these fail, the Router catches the error)
    state_risk_map, city_rules, bad_pins = await load_rules(db)
    bureau_cfg = load_bureau_config_from_json()
    risk_rules = await load_stability_config(db)

    # 2. Logic & Metrics
    tier = request.city_tier if request.city_tier in city_rules else "Rural"
    city_rule = city_rules[tier]
    state_risk = state_risk_map.get(request.state, "HIGH")

    debt_ratio = (
        request.existing_debt / request.monthly_income
        if request.monthly_income > 0
        else 1.0
    )
    max_eligible = request.monthly_income * city_rule["multiplier"]
    bureau_score = calculate_credit_score(request, debt_ratio, bureau_cfg)

    stability_rule = next(
        (
            r
            for r in risk_rules
            if r.min_credit_score <= bureau_score and r.max_dti_ratio is not None
        ),
        None,
    )

    # 3. Prepare & Evaluate Decision
    zen_input = {
        **request.model_dump(),
        "city_rule_min_income": city_rule["min_income"],
        "city_rule_multiplier": city_rule["multiplier"],
        "city_rule_rate": city_rule["rate"],
        "debt_ratio": debt_ratio,
        "bureau_score": bureau_score,
        "state_risk": state_risk,
        "pin_serviceable": request.pin_code not in bad_pins,
        "stability_max_dti_ratio": (
            stability_rule.max_dti_ratio if stability_rule else 0.5
        ),
    }

    # If GoRules fails, we want it to raise an error so we don't give a false 'REJECTED' status
    raw_result = decision_engine.evaluate(
        rules_path=str(RULES_FILE),
        input_data=zen_input,
    )
    result = raw_result.get("result", {})

    decision_label = result.get("decision_label", "REJECTED")
    approved_amount = result.get("approved_amount", 0)
    manual_review = result.get("manual_review", False)
    reason = result.get("reason", "No reason provided")

    # 4. Post-actions
    if decision_label == "APPROVED":
        try:
            # Note: create_loan_record should ideally be part of the main transaction,
            # but we keep this simple for now.
            notify_applicant(request, approved_amount, city_rule["rate"])
            loan_id = create_loan_record(
                db, request, approved_amount, city_rule["rate"]
            )
            generate_repayment_schedule(loan_id, approved_amount)
        except Exception as e:
            logger.error("Non-critical error in post-approval actions: %s", e)

    return {
        "decision": decision_label,
        "message": reason,
        "manual_review_required": manual_review,
        "guarantor_required": tier == "Rural",
        "credit_score": bureau_score,
        "approved_amount": approved_amount,
        "risk_assessment": get_risk_level(
            state_risk, debt_ratio, bureau_score, risk_rules
        ),
        "tier_applied": tier,
        "max_eligible_amount": max_eligible,
        "interest_rate": str(city_rule["rate"]),
    }
