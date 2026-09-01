from datetime import date
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from ..db_models import Laboratory, LaboratoryRecognition, Standard


class LaboratoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def _recognitions(self):
        return (
            select(LaboratoryRecognition)
            .options(joinedload(LaboratoryRecognition.laboratory), joinedload(LaboratoryRecognition.standard))
            .order_by(LaboratoryRecognition.laboratory_id, LaboratoryRecognition.standard_id)
        )

    def list_recognitions(self) -> list[LaboratoryRecognition]:
        return list(self.session.scalars(self._recognitions()))

    def search_recognitions(
        self,
        *,
        query: str = "",
        standard_number: str | None = None,
        location: str | None = None,
        as_of_date: date | None = None,
    ) -> list[LaboratoryRecognition]:
        statement = self._recognitions()
        if standard_number or (location and location.strip()):
            statement = statement.join(LaboratoryRecognition.laboratory).join(LaboratoryRecognition.standard)
        if standard_number:
            statement = statement.where(Standard.number == standard_number)
        if location and location.strip():
            location_pattern = f"%{location.strip()}%"
            statement = statement.where(
                or_(Laboratory.city.ilike(location_pattern), Laboratory.state.ilike(location_pattern))
            )
        records = list(self.session.scalars(statement))
        if as_of_date:
            records = [record for record in records if record.status == "RECOGNISED" and (record.valid_from is None or record.valid_from <= as_of_date) and (record.valid_until is None or record.valid_until >= as_of_date)]
        if query.strip():
            needle = query.strip().casefold()
            records = [
                record
                for record in records
                if needle
                in " ".join(
                    [
                        record.laboratory.name,
                        record.laboratory.city or "",
                        record.laboratory.state or "",
                        *(record.capabilities or []),
                    ]
                ).casefold()
            ]
        return records

    def for_standard(self, standard_id: str, as_of_date: date | None = None) -> list[LaboratoryRecognition]:
        records = list(self.session.scalars(self._recognitions().where(LaboratoryRecognition.standard_id == standard_id)))
        if as_of_date:
            records = [record for record in records if record.status == "RECOGNISED" and (record.valid_from is None or record.valid_from <= as_of_date) and (record.valid_until is None or record.valid_until >= as_of_date)]
        return records
