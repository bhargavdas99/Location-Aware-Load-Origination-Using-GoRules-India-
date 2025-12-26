"""
seed rule data

Revision ID: e2bad41618ea
Revises: e87df8b344b7
Create Date: 2025-12-26 14:52:37.546402
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e2bad41618ea"
down_revision: Union[str, Sequence[str], None] = "e87df8b344b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # -------------------------------------------------
    # STATE RISK
    # -------------------------------------------------
    state_risks = [
        ("Andhra Pradesh", "MEDIUM"),
        ("Arunachal Pradesh", "LOW"),
        ("Assam", "MEDIUM"),
        ("Bihar", "HIGH"),
        ("Chhattisgarh", "HIGH"),
        ("Goa", "LOW"),
        ("Gujarat", "LOW"),
        ("Haryana", "LOW"),
        ("Himachal Pradesh", "LOW"),
        ("Jharkhand", "HIGH"),
        ("Karnataka", "LOW"),
        ("Kerala", "MEDIUM"),
        ("Madhya Pradesh", "MEDIUM"),
        ("Maharashtra", "LOW"),
        ("Manipur", "MEDIUM"),
        ("Meghalaya", "LOW"),
        ("Mizoram", "LOW"),
        ("Nagaland", "MEDIUM"),
        ("Odisha", "HIGH"),
        ("Punjab", "MEDIUM"),
        ("Rajasthan", "MEDIUM"),
        ("Sikkim", "LOW"),
        ("Tamil Nadu", "LOW"),
        ("Telangana", "LOW"),
        ("Tripura", "LOW"),
        ("Uttar Pradesh", "HIGH"),
        ("Uttarakhand", "LOW"),
        ("West Bengal", "MEDIUM"),
    ]

    for state, risk in state_risks:
        conn.execute(
            sa.text(
                """
                INSERT INTO state_risk (state, risk_level)
                VALUES (:state, :risk)
                ON CONFLICT (state) DO NOTHING
                """
            ),
            {"state": state, "risk": risk},
        )

    # -------------------------------------------------
    # CITY RULES
    # -------------------------------------------------
    city_rules = [
        ("Metro", 20000, 8, "11%"),
        ("Tier1", 15000, 6, "12%"),
        ("Tier2", 12000, 5, "13%"),
        ("Rural", 10000, 3, "15%"),
    ]

    for tier, min_income, multiplier, rate in city_rules:
        conn.execute(
            sa.text(
                """
                INSERT INTO city_rules (tier, min_income, multiplier, rate)
                VALUES (:tier, :min_income, :multiplier, :rate)
                ON CONFLICT (tier) DO NOTHING
                """
            ),
            {
                "tier": tier,
                "min_income": min_income,
                "multiplier": multiplier,
                "rate": rate,
            },
        )

    # -------------------------------------------------
    # UNSERVICEABLE PINS
    # -------------------------------------------------
    pins = ["000000", "123456", "999999", "110099"]

    for pin in pins:
        conn.execute(
            sa.text(
                """
                INSERT INTO unserviceable_pins (pin_code)
                VALUES (:pin)
                ON CONFLICT (pin_code) DO NOTHING
                """
            ),
            {"pin": pin},
        )

    # -------------------------------------------------
    # RISK LEVEL RULES
    # -------------------------------------------------
    risk_level_rules = [
        ("HIGH", "HIGH", 700, 0.5),
        ("LOW", "LOW", 800, 0.3),
    ]

    for risk_level, state_risk, min_score, max_dti in risk_level_rules:
        conn.execute(
            sa.text(
                """
                INSERT INTO risk_level_rules
                (risk_level, state_risk, min_credit_score, max_dti_ratio)
                VALUES (:risk_level, :state_risk, :min_score, :max_dti)
                """
            ),
            {
                "risk_level": risk_level,
                "state_risk": state_risk,
                "min_score": min_score,
                "max_dti": max_dti,
            },
        )


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa.text("DELETE FROM risk_level_rules"))
    conn.execute(sa.text("DELETE FROM unserviceable_pins"))
    conn.execute(sa.text("DELETE FROM city_rules"))
    conn.execute(sa.text("DELETE FROM state_risk"))
