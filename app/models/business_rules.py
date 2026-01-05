from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class BusinessRule(Base):
    __tablename__ = "business_rules"

    # We use 'rule_key' as the primary key so we can easily look up "loan_decision"
    rule_key = Column(String, primary_key=True, index=True)
    content = Column(JSONB, nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())