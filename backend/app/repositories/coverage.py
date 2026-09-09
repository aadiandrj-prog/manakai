from __future__ import annotations

from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from ..db_models import CoverageRecord, HallmarkingCentre, HallmarkingGuidance, LaboratoryRecognition, ProductCategory, ProductFamily, SourceRecord


class CoverageRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[CoverageRecord]:
        statement = select(CoverageRecord).options(
            joinedload(CoverageRecord.product_category),
            joinedload(CoverageRecord.primary_standard),
            joinedload(CoverageRecord.regime),
        ).order_by(ProductCategory.name).join(CoverageRecord.product_category).where(CoverageRecord.lifecycle_status == "PUBLISHED")
        return list(self.session.scalars(statement))

    def for_category(self, slug: str) -> CoverageRecord | None:
        statement = select(CoverageRecord).join(CoverageRecord.product_category).options(
            joinedload(CoverageRecord.product_category), joinedload(CoverageRecord.primary_standard), joinedload(CoverageRecord.regime),
        ).where(ProductCategory.slug == slug, CoverageRecord.lifecycle_status == "PUBLISHED")
        return self.session.scalar(statement)

    def stats(self) -> dict:
        published = CoverageRecord.lifecycle_status == "PUBLISHED"
        rows = dict(self.session.execute(select(CoverageRecord.coverage_status, func.count()).where(published).group_by(CoverageRecord.coverage_status)).all())
        sources = self.session.scalar(select(func.count()).select_from(SourceRecord).where(SourceRecord.verification_status == "AUTHORITATIVE")) or 0
        standards = self.session.scalar(select(func.count(func.distinct(CoverageRecord.primary_standard_id))).where(published, CoverageRecord.primary_standard_id.is_not(None))) or 0
        today = date.today()
        labs = self.session.scalar(select(func.count()).select_from(LaboratoryRecognition).where(LaboratoryRecognition.status == "RECOGNISED", (LaboratoryRecognition.valid_until.is_(None) | (LaboratoryRecognition.valid_until >= today)))) or 0
        refreshed = self.session.scalar(select(func.max(CoverageRecord.last_refreshed_at)).where(published))
        return {
            "total": sum(rows.values()), "verified": rows.get("VERIFIED", 0), "partial": rows.get("PARTIAL", 0),
            "metadata_only": rows.get("METADATA_ONLY", 0), "unsupported": rows.get("UNSUPPORTED", 0),
            "authoritative_sources": sources, "current_standards": standards, "current_laboratory_scopes": labs, "last_refreshed_at": refreshed,
        }

    def family_for_slug(self, slug: str) -> ProductFamily | None:
        return self.session.scalar(select(ProductFamily).where(ProductFamily.slug == slug, ProductFamily.lifecycle_status == "PUBLISHED"))

    def hallmarking_centres(self, *, query: str = "", state: str | None = None, as_of_date: date | None = None) -> list[HallmarkingCentre]:
        statement = select(HallmarkingCentre).where(HallmarkingCentre.source_kind == "AUTHORITATIVE")
        if query.strip():
            pattern = f"%{query.strip()}%"
            statement = statement.where(or_(HallmarkingCentre.name.ilike(pattern), HallmarkingCentre.city.ilike(pattern), HallmarkingCentre.state.ilike(pattern)))
        if state:
            statement = statement.where(HallmarkingCentre.state.ilike(f"%{state.strip()}%"))
        records = list(self.session.scalars(statement.order_by(HallmarkingCentre.name)))
        if as_of_date:
            records = [item for item in records if item.status == "RECOGNISED" and (item.valid_from is None or item.valid_from <= as_of_date) and (item.valid_until is None or item.valid_until >= as_of_date)]
        return records

    def hallmarking_guidance(self) -> list[HallmarkingGuidance]:
        return list(self.session.scalars(select(HallmarkingGuidance).order_by(HallmarkingGuidance.topic)))
