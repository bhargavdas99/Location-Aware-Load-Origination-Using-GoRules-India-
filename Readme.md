# Loan Evaluation API

This project provides a **Location Based Loan Evaluation API** built with FastAPI. It evaluates loan requests based on multiple rules (state risk, city tier, credit score, etc.) using a GoRules engine and database-driven configuration.

---

## Features

- Evaluate loan applications with dynamic rules.
- Credit score calculation based on employment, debt ratio, and age.
- Risk assessment for loan approval.
- Database-driven configuration and rules.
- Post-approval actions: notify applicant, generate repayment schedule, create loan record.

---

## Project Structure

```

.
├── api                  # FastAPI endpoints
│   └── loan.py
├── core                 # Database configuration
│   └── database.py
├── models               # SQLAlchemy models
│   └── loan_models.py
├── rules                # Business rules
│   ├── loan_decision.json
│   └── loan_rules.py
├── schemas              # Pydantic request/response schemas
│   └── loan.py
├── services             # Service layer for actions & Zen engine
│   ├── los_post_actions.py
│   └── zen_engine.py
└── alembic              # Alembic migrations

````

---

## Installation

1. **Clone the repository**

```bash
git clone <repo-url>
cd <repo-folder>
````

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Database Setup

This project uses **PostgreSQL** as the database.

1. Create a new PostgreSQL database:

```sql
CREATE DATABASE loan_db;
```

2. Update the database URL in `core/database.py` (or `.env` if using environment variables):

```python
SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost:5432/loan_db"
```

---

## Alembic Migrations

1. **Initialize Alembic (if starting fresh)**

```bash
alembic init alembic
```

2. **Create initial tables**

```bash
alembic revision --autogenerate -m "Initial tables"
alembic upgrade head
```

3. **Seed initial data**

```bash
alembic revision -m "Seed rule data"  # Add your data insertion code
alembic upgrade head
```

* This will populate tables:

  * `state_risk`
  * `city_rules`
  * `unserviceable_pins`
  * `bureau_score_config`
  * `risk_level_rules`

---

## Running the API

```bash
uvicorn app.main:app --reload
```

* API will be available at `http://127.0.0.1:8000`
* Swagger docs: `http://127.0.0.1:8000/docs`

---

## API Endpoint

### POST `/loan/evaluate`

**Request Body:**

```json
{
  "age": 35,
  "monthly_income": 50000,
  "employment_duration_months": 36,
  "existing_debt": 10000,
  "loan_requested": 200000,
  "state": "Maharashtra",
  "city_tier": "Metro",
  "pin_code": "400001",
  "disaster_affected_area": false,
  "address_duration_months": 24,
  "work_location_matches_residence": true
}
```

**Response:**

```json
{
  "decision": "APPROVED",
  "reason": "Eligible for loan",
  "manual_review_required": false,
  "guarantor_required": false,
  "credit_score": 850,
  "approved_amount": 200000,
  "risk_assessment": "LOW",
  "tier_applied": "Metro",
  "max_eligible_amount": 400000,
  "interest_rate": "11%"
}
```

---

## Notes

* All rules and configurations are now **DB-driven**, including credit score parameters and risk rules.
* GoRules engine evaluates JSON-based rules.
* Alembic is used for database schema migrations and data seeding.

---
