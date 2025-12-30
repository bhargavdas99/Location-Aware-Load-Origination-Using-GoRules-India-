from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import json
import logging

from app.repositories.state_risk_repo import StateRiskRepository
from app.repositories.city_rule_repo import CityRuleRepository
from app.repositories.unserviceable_pin_repo import UnserviceablePinRepository
from app.repositories.risk_level_repo import RiskLevelRuleRepository

logger = logging.getLogger(__name__)


async def load_rules(session: AsyncSession):
    """
    Async load state risk, city rules, and unserviceable pins from DB.
    Exceptions are not caught here so the caller (API) can handle the failure.
    """
    state_risk_repo = StateRiskRepository(session)
    city_rule_repo = CityRuleRepository(session)
    unserviceable_pin_repo = UnserviceablePinRepository(session)

    # If these fail, they will raise an exception to the router
    state_risk_list = await state_risk_repo.get_all()
    city_rule_list = await city_rule_repo.get_all()
    unserviceable_pin_list = await unserviceable_pin_repo.get_all()

    state_risk = {r.state: r.risk_level for r in state_risk_list}

    city_rules = {
        r.tier: {
            "min_income": r.min_income,
            "multiplier": r.multiplier,
            "rate": r.rate,
        }
        for r in city_rule_list
    }

    unserviceable_pins = {r.pin_code for r in unserviceable_pin_list}

    return state_risk, city_rules, unserviceable_pins


async def load_stability_config(session: AsyncSession):
    """
    Async load risk level rules from DB.
    """
    risk_repo = RiskLevelRuleRepository(session)
    return await risk_repo.get_all()


def load_bureau_config_from_json() -> dict:
    """
    JSON file loader. Raises FileNotFoundError or JSONDecodeError if config is invalid.
    """
    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "rules"
        / "bureau_score_config.json"
    )

    # We use a context manager; if file is missing, the error bubbles up
    with open(config_path, "r") as f:
        return json.load(f)
