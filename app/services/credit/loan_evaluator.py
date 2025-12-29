from pathlib import Path
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

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
    try:
        # Load DB-backed rules (async)
        state_risk_map, city_rules, bad_pins = await load_rules(db)
        bureau_cfg = load_bureau_config_from_json()  # JSON load can remain sync
        risk_rules = await load_stability_config(db)

        # Resolve city tier
        tier = request.city_tier if request.city_tier in city_rules else "Rural"
        city_rule = city_rules[tier]
        state_risk = state_risk_map.get(request.state, "HIGH")

        # Derived metrics
        debt_ratio = (
            request.existing_debt / request.monthly_income
            if request.monthly_income > 0
            else 1.0
        )
        max_eligible = request.monthly_income * city_rule["multiplier"]

        # Calculate bureau score
        bureau_score = calculate_credit_score(request, debt_ratio, bureau_cfg)
        stability_rule = next(
            (
                r
                for r in risk_rules
                if r.min_credit_score <= bureau_score and r.max_dti_ratio is not None
            ),
            None,
        )

        # Prepare input for GoRules
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

        # Evaluate decision rules via GoRules
        try:
            raw_result = decision_engine.evaluate(
                rules_path=str(RULES_FILE),
                input_data=zen_input,
            )
            logger.info("Raw GoRules result: %s", raw_result)
            result = raw_result.get("result", {})
        except Exception as e:
            logger.error("Error evaluating GoRules decision: %s", e)
            result = {}

        decision_label = result.get("decision_label", "REJECTED")
        approved_amount = result.get("approved_amount", 0)
        manual_review = result.get("manual_review", False)
        reason = result.get("reason", "No reason provided")

        is_guarantor_required = tier == "Rural"

        # Post-actions
        if decision_label == "APPROVED":
            try:
                notify_applicant(request, approved_amount, city_rule["rate"])
                loan_id = create_loan_record(
                    db, request, approved_amount, city_rule["rate"]
                )
                generate_repayment_schedule(loan_id, approved_amount)
            except Exception as e:
                logger.error("Error during post-approval actions: %s", e)

        # Final response
        return {
            "decision": decision_label,
            "message": reason,
            "manual_review_required": manual_review,
            "guarantor_required": is_guarantor_required,
            "credit_score": bureau_score,
            "approved_amount": approved_amount,
            "risk_assessment": get_risk_level(
                state_risk, debt_ratio, bureau_score, risk_rules
            ),
            "tier_applied": tier,
            "max_eligible_amount": max_eligible,
            "interest_rate": str(city_rule["rate"]),  # ensure string for Pydantic
        }

    except Exception as e:
        logger.error("Unexpected error in loan evaluation: %s", e)
        # return all required fields to satisfy Pydantic validation
        return {
            "decision": "ERROR",
            "message": "Internal server error.",
            "manual_review_required": False,
            "guarantor_required": False,
            "credit_score": 0,
            "approved_amount": 0,
            "risk_assessment": "UNKNOWN",
            "tier_applied": "UNKNOWN",
            "max_eligible_amount": 0,
            "interest_rate": "0.0",
        }
