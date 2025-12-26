from sqlalchemy.orm import Session

from app.models.state_risk import StateRisk
from app.models.city_rules import CityRule
from app.models.unserviceable_pin import UnserviceablePin
from app.models.bureau_score_config import BureauScoreConfig
from app.models.risk_level import RiskLevelRule


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


def load_bureau_config(session: Session) -> BureauScoreConfig:
    return session.query(BureauScoreConfig).first()


def load_stability_config(session: Session) -> list[RiskLevelRule]:
    return session.query(RiskLevelRule).all()
