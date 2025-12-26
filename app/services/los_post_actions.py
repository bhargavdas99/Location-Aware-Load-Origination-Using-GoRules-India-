import logging
from datetime import date, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def notify_applicant(application, approved_amount, interest_rate):
    logger.info(
        f"[NOTIFICATION] Loan APPROVED | "
        f"Amount: {approved_amount} | "
        f"Rate: {interest_rate} | "
        f"Applicant PIN: {application.pin_code}"
    )


def create_loan_record(db, application, approved_amount, interest_rate):
    loan_id = f"LN-{application.pin_code}-{approved_amount}"
    logger.info(
        f"[CORE BANKING] Loan created | LoanID: {loan_id} | Amount: {approved_amount} | Rate: {interest_rate}"
    )
    return loan_id


def generate_repayment_schedule(loan_id, approved_amount, tenure_months=24):
    emi = round(approved_amount / tenure_months, 2)
    schedule = []
    start_date = date.today() + timedelta(days=30)

    for i in range(tenure_months):
        schedule.append(
            {
                "loan_id": loan_id,
                "installment_no": i + 1,
                "emi": emi,
                "due_date": start_date + timedelta(days=30 * i),
            }
        )

    logger.info(
        f"[REPAYMENT] Schedule generated | LoanID: {loan_id} | EMI: {emi} | Tenure: {tenure_months} months"
    )
    return schedule
