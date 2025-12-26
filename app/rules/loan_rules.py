from sqlalchemy.orm import Session

from app.models.loan_models import (
    StateRisk,
    CityRule,
    UnserviceablePin,
    BureauScoreConfig,
    RiskLevelRule,
)


# LOAD DB-BACKED RULES
def load_rules(session: Session):
    state_risk = {r.state: r.risk_level for r in session.query(StateRisk).all()}

    city_rules = {
        r.tier: {
            "min_income": r.min_income,
            "multiplier": r.multiplier,
            "rate": r.rate,
        }
        for r in session.query(CityRule).all()
    }

    unserviceable_pins = {r.pin_code for r in session.query(UnserviceablePin).all()}

    return state_risk, city_rules, unserviceable_pins


# LOAD CONFIG TABLES
def load_bureau_config(session: Session) -> BureauScoreConfig:
    return session.query(BureauScoreConfig).first()


def load_stability_config(session: Session):
    risk_rules = session.query(RiskLevelRule).all()
    return risk_rules


# CREDIT SCORE CALCULATION
def calculate_credit_score(data, debt_ratio, cfg: BureauScoreConfig) -> int:
    score = cfg.base_score

    # Debt ratio impact
    if debt_ratio <= cfg.debt_low_threshold:
        score += cfg.debt_low_bonus
    elif debt_ratio <= cfg.debt_medium_threshold:
        score += cfg.debt_medium_bonus
    elif debt_ratio > cfg.debt_high_threshold:
        score = cfg.debt_high_penalty

    # Employment stability
    if data.employment_duration_months >= cfg.emp_long_months:
        score += cfg.emp_long_bonus
    elif data.employment_duration_months >= cfg.emp_medium_months:
        score += cfg.emp_medium_bonus
    elif data.employment_duration_months < cfg.emp_short_months:
        score = cfg.emp_short_penalty

    # Age factor
    if cfg.age_min <= data.age <= cfg.age_max:
        score += cfg.age_bonus

    return max(cfg.score_min, min(cfg.score_max, score))


# RISK LEVEL DECISION
def get_risk_level(
    state_risk: str,
    debt_ratio: float,
    bureau_score: int,
    risk_rules: list[RiskLevelRule],
) -> str:
    for rule in risk_rules:
        if (
            state_risk == rule.state_risk
            and bureau_score >= rule.min_credit_score
            and debt_ratio <= rule.max_dti_ratio
        ):
            return rule.risk_level

    return "MEDIUM"
