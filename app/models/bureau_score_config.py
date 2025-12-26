from sqlalchemy import Column, Integer, String, Float, Boolean
from app.core.database import Base


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
