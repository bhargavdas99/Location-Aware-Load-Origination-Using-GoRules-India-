from pydantic import BaseModel, Field


class LoanRequest(BaseModel):
    # Required and must be exactly 10 characters (Standard PAN length)
    pan_number: str = Field(..., min_length=10, max_length=10)

    # Numeric constraints ensure we don't get impossible data
    age: int = Field(..., gt=18)  # Must be greater than 18
    monthly_income: float = Field(..., gt=0)  # Must be a positive number

    employment_duration_months: int = Field(..., ge=0)
    existing_debt: float = Field(..., ge=0)
    loan_requested: float = Field(..., gt=0)

    state: str = Field(..., min_length=2)
    city: str = Field(..., min_length=2)
    city_tier: str

    pin_code: str = Field(..., min_length=6, max_length=6)

    disaster_affected_area: bool = Field(...)  # Ellipsis makes it explicitly mandatory
    address_duration_months: int = Field(..., ge=0)
    work_location_matches_residence: bool = Field(...)


class LoanResponse(BaseModel):
    decision: str
    message: str
    manual_review_required: bool
    guarantor_required: bool
    credit_score: int
    approved_amount: float
    risk_assessment: str
    tier_applied: str
    max_eligible_amount: float
    interest_rate: str
