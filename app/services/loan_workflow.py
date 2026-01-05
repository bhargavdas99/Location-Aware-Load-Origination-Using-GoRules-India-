from statemachine import StateMachine, State

class LoanWorkflow(StateMachine):
    def __init__(self, model):
        super().__init__(model, state_field="status")

    # internal api1 -> internal api2 -> cibil score api -> (auto approve/reject or pending review) -> (manual approve/reject)
    # States
    submitted = State("submitted", initial=True)
    api1_done = State("api1_done") #internal api1
    api2_done = State("api2_done") #internal api2
    cibil_done = State("cibil_done") #cibil score api
    
    pending_review = State("pending_review")
    approved = State("approved", final=True)
    rejected = State("rejected", final=True)

    # Transitions
    validate_api1 = submitted.to(api1_done)
    validate_api2 = api1_done.to(api2_done)
    fetch_cibil = api2_done.to(cibil_done)
    
    to_review = cibil_done.to(pending_review)
    to_approve = cibil_done.to(approved) | pending_review.to(approved)
    to_reject = cibil_done.to(rejected) | pending_review.to(rejected)