from sqlalchemy import Column, Integer, String
from app.core.database import Base


class UnserviceablePin(Base):
    __tablename__ = "unserviceable_pins"

    id = Column(Integer, primary_key=True)
    pin_code = Column(String, unique=True)
