from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base


class CityRule(Base):
    __tablename__ = "city_rules"

    id = Column(Integer, primary_key=True)
    tier = Column(String, unique=True, nullable=False)
    min_income = Column(Float)
    multiplier = Column(Integer)
    rate = Column(String)
