from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db_models import QCO, StandardQCO


class QCORepository:
    def __init__(self, session: Session):
        self.session = session

    def for_standard(self, standard_id: str) -> list[QCO]:
        statement = (
            select(QCO)
            .join(StandardQCO, StandardQCO.qco_id == QCO.id)
            .where(StandardQCO.standard_id == standard_id)
            .order_by(QCO.source_verified.desc(), QCO.effective_date.desc().nullslast())
        )
        return list(self.session.scalars(statement))
