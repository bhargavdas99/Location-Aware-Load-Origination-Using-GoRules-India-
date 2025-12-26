from sqlalchemy import Column, Integer, String, Float, Boolean
from app.core.database import Base


class StateRisk(Base):
    __tablename__ = "state_risk"

    id = Column(Integer, primary_key=True)
    state = Column(String, unique=True, nullable=False)
    risk_level = Column(String, nullable=False)


class CityRule(Base):
    __tablename__ = "city_rules"

    id = Column(Integer, primary_key=True)
    tier = Column(String, unique=True, nullable=False)
    min_income = Column(Float)
    multiplier = Column(Integer)
    rate = Column(String)


class UnserviceablePin(Base):
    __tablename__ = "unserviceable_pins"

    id = Column(Integer, primary_key=True)
    pin_code = Column(String, unique=True)


class BureauScoreConfig(Base):
    __tablename__ = "bureau_score_config"

    id = Column(Integer, primary_key=True)

    # Base score
    base_score = Column(Integer, nullable=False)

    # Debt ratio rules
    debt_low_threshold = Column(Float, nullable=False)
    debt_low_bonus = Column(Integer, nullable=False)

    debt_medium_threshold = Column(Float, nullable=False)
    debt_medium_bonus = Column(Integer, nullable=False)

    debt_high_threshold = Column(Float, nullable=False)
    debt_high_penalty = Column(Integer, nullable=False)

    # Employment rules
    emp_long_months = Column(Integer, nullable=False)
    emp_long_bonus = Column(Integer, nullable=False)

    emp_medium_months = Column(Integer, nullable=False)
    emp_medium_bonus = Column(Integer, nullable=False)

    emp_short_months = Column(Integer, nullable=False)
    emp_short_penalty = Column(Integer, nullable=False)

    # Age rules
    age_min = Column(Integer, nullable=False)
    age_max = Column(Integer, nullable=False)
    age_bonus = Column(Integer, nullable=False)

    # Score limits
    score_min = Column(Integer, nullable=False)
    score_max = Column(Integer, nullable=False)


class RiskLevelRule(Base):
    __tablename__ = "risk_level_rules"

    id = Column(Integer, primary_key=True)

    # HIGH / LOW / MEDIUM
    risk_level = Column(String, nullable=False)

    # Conditions
    state_risk = Column(String, nullable=False)  # HIGH / LOW
    min_credit_score = Column(Integer, nullable=False)
    max_dti_ratio = Column(Float, nullable=False)
