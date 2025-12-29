import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


# Load Bureau Score config from JSON
def load_bureau_config_from_json() -> dict:
    try:
        config_path = (
            Path(__file__).resolve().parent.parent.parent
            / "rules"
            / "bureau_score_config.json"
        )
        with open(config_path, "r") as f:
            cfg = json.load(f)
        return cfg
    except FileNotFoundError as e:
        logger.error("Bureau config file not found: %s", e)
        return {}
    except json.JSONDecodeError as e:
        logger.error("Error parsing bureau config JSON: %s", e)
        return {}


def calculate_credit_score(data, debt_ratio, cfg: dict) -> int:
    try:
        """
        Calculates the credit score based on the JSON configuration dictionary.
        """
        score = cfg["base_score"]

        # Debt ratio impact
        if debt_ratio <= cfg["debt_low_threshold"]:
            score += cfg["debt_low_bonus"]
        elif debt_ratio <= cfg["debt_medium_threshold"]:
            score += cfg["debt_medium_bonus"]
        elif debt_ratio > cfg["debt_high_threshold"]:
            score = cfg["debt_high_penalty"]

        # Employment stability
        if data.employment_duration_months >= cfg["emp_long_months"]:
            score += cfg["emp_long_bonus"]
        elif data.employment_duration_months >= cfg["emp_medium_months"]:
            score += cfg["emp_medium_bonus"]
        elif data.employment_duration_months < cfg["emp_short_months"]:
            score = cfg["emp_short_penalty"]

        # Age factor
        if cfg["age_min"] <= data.age <= cfg["age_max"]:
            score += cfg["age_bonus"]

        # Ensure score within min/max
        return max(cfg["score_min"], min(cfg["score_max"], score))
    except Exception as e:
        logger.error("Error calculating credit score: %s", e)
        return cfg.get("base_score", 0)
