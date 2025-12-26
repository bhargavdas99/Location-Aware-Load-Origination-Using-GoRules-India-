from app.models.bureau_score_config import BureauScoreConfig


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
