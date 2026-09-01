from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db_models import QCO, QCOApplicability, StandardQCO


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

    def resolve(self, *, standard_id: str, product_category: str, enterprise_category: str):
        statement = (
            select(QCO, QCOApplicability)
            .join(StandardQCO, StandardQCO.qco_id == QCO.id)
            .join(QCOApplicability, QCOApplicability.qco_id == QCO.id)
            .where(
                StandardQCO.standard_id == standard_id,
                QCOApplicability.covered_product_category == product_category,
                QCOApplicability.enterprise_category == enterprise_category,
            )
            .order_by(QCO.notification_date.desc().nullslast())
        )
        return self.session.execute(statement).first()
