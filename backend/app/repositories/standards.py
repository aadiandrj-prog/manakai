from __future__ import annotations

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, joinedload

from ..db_models import CertificationScheme, Standard, StandardRelationship, Test


class StandardRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[Standard]:
        return list(self.session.scalars(select(Standard).order_by(Standard.number, Standard.version)))

    def search(self, query: str) -> list[Standard]:
        cleaned = query.strip()
        if not cleaned:
            return self.list()
        term_filters = []
        for term in cleaned.split():
            pattern = f"%{term}%"
            term_filters.append(
                or_(
                    Standard.number.ilike(pattern),
                    Standard.title.ilike(pattern),
                    Standard.category.ilike(pattern),
                    Standard.scope.ilike(pattern),
                )
            )
        statement = select(Standard).where(
            and_(*term_filters)
        ).order_by(Standard.number)
        return list(self.session.scalars(statement))

    def get(self, standard_id: str) -> Standard | None:
        return self.session.get(Standard, standard_id)

    def relationships(self, standard_id: str) -> list[StandardRelationship]:
        statement = (
            select(StandardRelationship)
            .options(joinedload(StandardRelationship.target))
            .where(StandardRelationship.source_standard_id == standard_id)
            .order_by(StandardRelationship.relationship_type)
        )
        return list(self.session.scalars(statement))

    def tests_for(self, standard_id: str) -> list[Test]:
        return list(self.session.scalars(select(Test).where(Test.standard_id == standard_id).order_by(Test.name)))

    def scheme_for(self, standard_id: str) -> CertificationScheme | None:
        return self.session.scalar(select(CertificationScheme).where(CertificationScheme.standard_id == standard_id))
