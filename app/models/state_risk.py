from sqlalchemy import Column, Integer, String
from app.core.database import Base


class StateRisk(Base):
    __tablename__ = "state_risk"

    id = Column(Integer, primary_key=True)
    state = Column(String, unique=True, nullable=False)
    risk_level = Column(String, nullable=False)
