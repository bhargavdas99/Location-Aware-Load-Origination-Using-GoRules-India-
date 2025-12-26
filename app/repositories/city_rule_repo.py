from sqlalchemy.orm import Session
from app.models.city_rules import CityRule


class CityRuleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        return self.session.query(CityRule).all()
