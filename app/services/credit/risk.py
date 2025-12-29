from app.models.risk_level import RiskLevelRule
import logging

logger = logging.getLogger(__name__)


def get_risk_level(
    state_risk: str,
    debt_ratio: float,
    bureau_score: int,
    risk_rules: list[RiskLevelRule],
) -> str:
    try:
        for rule in risk_rules:
            if (
                state_risk == rule.state_risk
                and bureau_score >= rule.min_credit_score
                and debt_ratio <= rule.max_dti_ratio
            ):
                return rule.risk_level
        return "MEDIUM"
    except Exception as e:
        logger.error("Error evaluating risk level: %s", e)
        return "MEDIUM"
