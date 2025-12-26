from pydantic import BaseModel, constr


class LoanRequest(BaseModel):
    age: int
    monthly_income: float
    employment_duration_months: int
    existing_debt: float
    loan_requested: float
    state: str
    city_tier: str
    pin_code: constr(min_length=6, max_length=6)  # type: ignore # Only 6-digit pincodes allowed
    disaster_affected_area: bool
    address_duration_months: int
    work_location_matches_residence: bool


class LoanResponse(BaseModel):
    decision: str
    reason: str
    manual_review_required: bool
    guarantor_required: bool
    credit_score: int
    approved_amount: float
    risk_assessment: str
    tier_applied: str
    max_eligible_amount: float
    interest_rate: str
