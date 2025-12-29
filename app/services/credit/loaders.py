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
    Async load state risk, city rules, and unserviceable pins from DB via repositories
    """
    try:
        state_risk_repo = StateRiskRepository(session)
        city_rule_repo = CityRuleRepository(session)
        unserviceable_pin_repo = UnserviceablePinRepository(session)

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
    except Exception as e:
        logger.error("Error loading rules from DB: %s", e)
        return {}, {}, set()


async def load_stability_config(session: AsyncSession):
    """
    Async load risk level rules from DB via repository
    """
    try:
        risk_repo = RiskLevelRuleRepository(session)
        return await risk_repo.get_all()
    except Exception as e:
        logger.error("Error loading risk rules from DB: %s", e)
        return []


def load_bureau_config_from_json() -> dict:
    """
    JSON file loader remains sync
    """
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
