from sqlalchemy.orm import Session
from app.models.unserviceable_pin import UnserviceablePin


class UnserviceablePinRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        return self.session.query(UnserviceablePin).all()
