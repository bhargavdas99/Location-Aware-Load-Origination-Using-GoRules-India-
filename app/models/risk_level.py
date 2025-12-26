from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base


class RiskLevelRule(Base):
    __tablename__ = "risk_level_rules"

    id = Column(Integer, primary_key=True)

    # HIGH / LOW / MEDIUM
    risk_level = Column(String, nullable=False)

    # Conditions
    state_risk = Column(String, nullable=False)  # HIGH / LOW
    min_credit_score = Column(Integer, nullable=False)
    max_dti_ratio = Column(Float, nullable=False)
