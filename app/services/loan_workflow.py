from statemachine import StateMachine, State


class LoanWorkflow(StateMachine):
    def __init__(self, model):
        super().__init__(model, state_field="status")

    # Define States
    submitted = State("submitted", initial=True)
    pending_review = State("pending_review")

    # Marked as final to prevent further transitions
    approved = State("approved", final=True)
    rejected = State("rejected", final=True)

    # Transitions
    to_review = submitted.to(pending_review)
    to_approve = submitted.to(approved) | pending_review.to(approved)
    to_reject = submitted.to(rejected) | pending_review.to(rejected)
