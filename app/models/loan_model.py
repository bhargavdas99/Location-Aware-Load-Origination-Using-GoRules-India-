import uuid
from sqlalchemy import Column, String, Float, Integer, JSON, Boolean, DateTime
from app.core.database import Base
from sqlalchemy.sql import func


def generate_uuid():
    return str(uuid.uuid4())


class LoanRecord(Base):
    __tablename__ = "loans"

    # default=generate_uuid ensures a new id/primary_key is created for every new record
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    pan_number = Column(String, index=True)
    status = Column(String, default="submitted")
    bureau_score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # --- Request Fields (Mirroring LoanRequest) ---
    age = Column(Integer)
    monthly_income = Column(Float)
    employment_duration_months = Column(Integer)
    existing_debt = Column(Float)
    loan_requested = Column(Float)
    state = Column(String)
    city = Column(String)
    city_tier = Column(String)
    pin_code = Column(String(6))
    disaster_affected_area = Column(Boolean)
    address_duration_months = Column(Integer)
    work_location_matches_residence = Column(Boolean)

    # --- Result Fields (Mirroring LoanResponse) ---
    approved_amount = Column(Float, default=0.0)
    risk_assessment = Column(String, nullable=True)
    interest_rate = Column(String, nullable=True)

    # Storage for the full GoRules result object
    decision_metadata = Column(JSON, nullable=True)

    version_id = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version_id}
