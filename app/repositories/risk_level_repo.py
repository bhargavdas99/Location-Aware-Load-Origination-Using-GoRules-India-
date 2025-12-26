from sqlalchemy.orm import Session
from app.models.risk_level import RiskLevelRule


class RiskLevelRuleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        return self.session.query(RiskLevelRule).all()
