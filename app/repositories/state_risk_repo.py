from sqlalchemy.orm import Session
from app.models.state_risk import StateRisk


class StateRiskRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        return self.session.query(StateRisk).all()
