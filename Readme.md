# Loan Evaluation API

This project provides a **Location-Aware Loan Evaluation API** built with **FastAPI**.
It evaluates loan applications using **database-driven configurations**, **credit scoring logic**, and a **GoRules (Zen) decision engine** for final approval decisions.

The system is designed to be **scalable, modular, and production-ready**, following clean service-layer architecture.

---

## Key Features

* Location-based loan evaluation (state risk, city tier, PIN serviceability)
* Credit score calculation using configurable bureau rules
* Risk assessment based on state risk, credit score, and debt ratio
* GoRules (Zen Engine) for declarative loan decision logic
* Database-driven rules & configurations
* Post-approval actions:

  * Applicant notification
  * Loan record creation
  * Repayment schedule generation
* Fully managed schema & data migrations using Alembic

---

## Updated Project Structure

```
.
├── api/                         # FastAPI route handlers (thin controllers)
│   └── loan.py
├── core/                        # Core infrastructure (DB, settings)
│   └── database.py
├── models/                      # SQLAlchemy ORM models (DB schema only)
│   ├── city_rules.py
│   ├── risk_level.py
│   ├── state_risk.py
│   └── unserviceable_pin.py
├── repositories/                # Data access layer (DB / JSON abstraction)
│   ├── city_rule_repo.py
│   ├── risk_level_repo.py
│   ├── state_risk_repo.py
│   └── unserviceable_pin_repo.py
├── schemas/                     # Pydantic request/response schemas
│   └── loan.py
├── services/                    # Business logic & orchestration
│   ├── credit/
│   │   ├── loaders.py           # Repository-based rule loaders
│   │   ├── scoring.py           # Credit score calculation
│   │   ├── risk.py              # Risk level determination
│   │   ├── loan_evaluator.py    # End-to-end evaluation flow
│   │   └── __init__.py
│   ├── los_post_actions.py      # Post-approval workflows
│   └── zen_engine.py            # GoRules (Zen) engine integration
├── rules/                       # Declarative rule & config files
│   ├── loan_decision.json       # GoRules decision rules
│   └── bureau_score_config.json # Bureau scoring configuration (JSON-based)
└── alembic/                     # Alembic migrations (schema + seed data)
```

### Design Notes

* `api/` contains **only orchestration logic**
* `services/` contains **all executable business logic**
* `rules/` is reserved for **declarative rule definitions (JSON / DSL)**
* Alembic migrations are **committed to Git** (never gitignored)

---

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd <repo-folder>
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Database Setup

This project uses **PostgreSQL**.

### 1. Create the database

```sql
CREATE DATABASE loan_db;
```

### 2. Configure database URL

Set the database URL via environment variables (recommended):

```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/loan_db"
```

Or configure it directly in `core/database.py`.

---

## Alembic Migrations

Alembic is used for **both schema management and rule data seeding**.

### Apply migrations

```bash
alembic upgrade head
```

### Create a new migration

```bash
alembic revision --autogenerate -m "your message"
```

### Tables managed via migrations

* `state_risk`
* `city_rules`
* `unserviceable_pins`
* `bureau_score_config`
* `risk_level_rules`

> ⚠️ **Important:**
> The `alembic/` folder **must be committed** to Git.
> Migration scripts are part of the application’s source of truth.

---

## Running the API

```bash
uvicorn app.main:app --reload
```

* API base URL: `http://127.0.0.1:8000`
* Swagger UI: `http://127.0.0.1:8000/docs`

---

## API Endpoint

### POST `/loan/evaluate`

#### Request Body

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

#### Response

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

## Processing Flow (High Level)

1. API receives loan request
2. DB-backed rules and configs are loaded
3. Credit score is calculated
4. Input is prepared for GoRules engine
5. GoRules evaluates approval decision
6. Risk level is determined
7. Post-approval workflows are triggered (if applicable)
8. Final response is returned
