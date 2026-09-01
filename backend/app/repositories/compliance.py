from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..db_models import Citation, ComplianceJourney, ComplianceProfile, ComplianceProfileStandard, ProductProfile


class ComplianceRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, profile_id: str) -> ComplianceProfile | None:
        statement = (
            select(ComplianceProfile)
            .options(
                joinedload(ComplianceProfile.product_profile).joinedload(ProductProfile.product),
                joinedload(ComplianceProfile.qco),
                joinedload(ComplianceProfile.certification_scheme),
            )
            .where(ComplianceProfile.id == profile_id)
        )
        return self.session.scalar(statement)

    def standard_ids(self, profile_id: str) -> list[str]:
        return list(self.session.scalars(select(ComplianceProfileStandard.standard_id).where(ComplianceProfileStandard.compliance_profile_id == profile_id)))

    def journey(self, profile_id: str) -> ComplianceJourney | None:
        return self.session.scalar(select(ComplianceJourney).where(ComplianceJourney.compliance_profile_id == profile_id))

    def create(
        self,
        *,
        product_profile_id: str,
        standard_id: str,
        additional_standard_ids: list[str] | None = None,
        confidence: float,
        mandatory_status: str,
        qco_id: str | None,
        certification_scheme_id: str | None,
        tests: list[str],
        required_documents: list[str],
        warnings: list[str],
        journey_steps: list[dict],
        as_of_date=None,
        data_mode: str = "DEMO",
        explanation_tree: dict | None = None,
    ) -> ComplianceProfile:
        profile_id = f"compliance-{uuid4().hex}"
        profile = ComplianceProfile(
            id=profile_id,
            product_profile_id=product_profile_id,
            confidence=confidence,
            mandatory_status=mandatory_status,
            qco_id=qco_id,
            certification_scheme_id=certification_scheme_id,
            tests=tests,
            required_documents=required_documents,
            warnings=warnings,
            as_of_date=as_of_date,
            data_mode=data_mode,
            explanation_tree=explanation_tree or {},
        )
        self.session.add(profile)
        self.session.flush()
        links = [ComplianceProfileStandard(id=f"profile-standard-{uuid4().hex}", compliance_profile_id=profile_id, standard_id=item) for item in [standard_id, *(additional_standard_ids or [])]]
        self.session.add_all([*links, ComplianceJourney(id=f"journey-{uuid4().hex}", compliance_profile_id=profile_id, steps=journey_steps)])
        self.session.flush()
        return profile

    def attach_citations(self, profile_id: str, citation_templates: list[Citation]) -> None:
        for template in citation_templates:
            self.session.add(
                Citation(
                    id=f"citation-{uuid4().hex}",
                    compliance_profile_id=profile_id,
                    document_id=template.document_id,
                    chunk_id=template.chunk_id,
                    claim=template.claim,
                    source_kind=template.source_kind,
                    validation_status=template.validation_status,
                    validation_error=template.validation_error,
                )
            )

    def attach_evidence(self, profile_id: str, *, document_id: str, chunk_id: str, claim: str, source_kind: str) -> Citation:
        citation = Citation(
            id=f"citation-{uuid4().hex}", compliance_profile_id=profile_id, document_id=document_id,
            chunk_id=chunk_id, claim=claim, source_kind=source_kind, validation_status="PENDING",
        )
        self.session.add(citation)
        self.session.flush()
        return citation
