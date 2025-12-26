from sqlalchemy.orm import Session
from pathlib import Path
import json

from app.repositories.state_risk_repo import StateRiskRepository
from app.repositories.city_rule_repo import CityRuleRepository
from app.repositories.unserviceable_pin_repo import UnserviceablePinRepository
from app.repositories.risk_level_repo import RiskLevelRuleRepository


def load_rules(session: Session):
    """Load state risk, city rules, and unserviceable pins from DB via repositories"""
    state_risk_repo = StateRiskRepository(session)
    city_rule_repo = CityRuleRepository(session)
    unserviceable_pin_repo = UnserviceablePinRepository(session)

    state_risk = {r.state: r.risk_level for r in state_risk_repo.get_all()}

    city_rules = {
        r.tier: {
            "min_income": r.min_income,
            "multiplier": r.multiplier,
            "rate": r.rate,
        }
        for r in city_rule_repo.get_all()
    }

    unserviceable_pins = {r.pin_code for r in unserviceable_pin_repo.get_all()}

    return state_risk, city_rules, unserviceable_pins


def load_bureau_config_from_json() -> dict:
    """Load bureau score configuration from JSON file instead of DB"""
    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "rules"
        / "bureau_score_config.json"
    )
    with open(config_path, "r") as f:
        cfg = json.load(f)
    return cfg


def load_stability_config(session: Session):
    """Load risk level rules via repository"""
    risk_repo = RiskLevelRuleRepository(session)
    return risk_repo.get_all()
