from sqlalchemy.orm import Session

from ..repositories import (
    ComplianceRepository,
    DocumentRepository,
    LaboratoryRepository,
    ProductRepository,
    QCORepository,
    StandardRepository,
)
from ..schemas import ComplianceProfile, JourneyStep, ProductAnalyseRequest, ProductProfile
from ..serializers import citation_to_schema, recognitions_to_laboratories, standard_to_schema
from .rules import QCORecord, evaluate_certification


class ComplianceService:
    def __init__(self, session: Session):
        self.session = session
        self.standards = StandardRepository(session)
        self.laboratories = LaboratoryRepository(session)
        self.qcos = QCORepository(session)
        self.products = ProductRepository(session)
        self.documents = DocumentRepository(session)
        self.compliance = ComplianceRepository(session)

    @staticmethod
    def classify(description: str) -> tuple[str, str, list[str], float]:
        text = description.casefold()
        if "kettle" in text or "boil" in text:
            return "is-302-2-15", "Household electrical appliance", ["Electric heating", "Household use"], 0.86
        if "helmet" in text:
            return "is-4151", "Protective rider equipment", ["Head protection", "Two-wheeler use"], 0.84
        if "steel" in text or "rebar" in text:
            return "is-1786", "Construction reinforcement material", ["Deformed bar", "Concrete reinforcement"], 0.82
        return "is-10322-5-8", "Electrical lighting equipment", ["Portable", "Rechargeable battery", "LED light source", "Emergency use"], 0.91

    def analyse(self, request: ProductAnalyseRequest) -> ComplianceProfile:
        standard_id, category, attributes, confidence = self.classify(request.description)
        standard = self.standards.get(standard_id)
        if standard is None:
            raise LookupError("Seeded candidate standard is missing")
        qcos = self.qcos.for_standard(standard_id)
        qco = qcos[0] if qcos else None
        mandatory_status = evaluate_certification(
            QCORecord(standard.number, qco.effective_date, qco.status, qco.source_verified)
            if qco
            else None
        )
        tests = [test.name for test in self.standards.tests_for(standard_id)]
        scheme = self.standards.scheme_for(standard_id)
        missing_attributes = ["rated voltage", "installation type", "battery chemistry"]
        product_profile = self.products.create_profile(
            name=request.description.strip(),
            category=category,
            role=request.role,
            description=request.description.strip(),
            language=request.language,
            attributes=attributes,
            missing_attributes=missing_attributes,
        )
        journey = self._journey(standard.number, category)
        warnings = ["DEMO_MODE is active.", "Mandatory status and effective dates are not verified."]
        profile = self.compliance.create(
            product_profile_id=product_profile.id,
            standard_id=standard.id,
            confidence=confidence,
            mandatory_status=mandatory_status,
            qco_id=qco.id if qco else None,
            certification_scheme_id=scheme.id if scheme else None,
            tests=tests or ["Product-specific test mapping unavailable"],
            required_documents=["Product specification", "Critical component list", "Circuit diagram", "Manufacturing process flow"],
            warnings=warnings,
            journey_steps=[step.model_dump() for step in journey],
        )
        templates = self.documents.search_citations(standard.number)
        self.compliance.attach_citations(profile.id, templates)
        self.session.commit()
        return self.get(profile.id)

    def get(self, profile_id: str) -> ComplianceProfile:
        profile = self.compliance.get(profile_id)
        if profile is None:
            raise LookupError("Compliance profile not found")
        standard_ids = self.compliance.standard_ids(profile_id)
        standards = [standard for standard_id in standard_ids if (standard := self.standards.get(standard_id))]
        recognitions = self.laboratories.for_standard(standards[0].id) if standards else []
        citations = self.documents.citations_for_profile(profile_id)
        journey = self.compliance.journey(profile_id)
        product_profile = profile.product_profile
        product = product_profile.product
        qco_label = None
        if profile.qco:
            qco_label = f"{profile.qco.title} ({profile.qco.source_kind}, {'verified' if profile.qco.source_verified else 'unverified'})"
        return ComplianceProfile(
            id=profile.id,
            product=ProductProfile(
                interpreted_product=product_profile.input_description or product.name,
                role=product_profile.role,
                category=product.category or "Unclassified",
                attributes=list(product_profile.attributes or []),
                missing_attributes=list(product_profile.missing_attributes or []),
            ),
            applicable_standards=[standard_to_schema(standard) for standard in standards],
            mandatory_status=profile.mandatory_status,
            qco=qco_label,
            certification_scheme=profile.certification_scheme.name if profile.certification_scheme else None,
            tests=list(profile.tests or []),
            required_documents=list(profile.required_documents or []),
            laboratories=recognitions_to_laboratories(recognitions),
            next_steps=[JourneyStep.model_validate(step) for step in (journey.steps if journey else [])],
            evidence=[citation_to_schema(citation) for citation in citations],
            confidence=profile.confidence,
            warnings=list(profile.warnings or []),
        )

    def journey(self, profile_id: str) -> list[JourneyStep]:
        journey = self.compliance.journey(profile_id)
        if journey is None:
            raise LookupError("Compliance journey not found")
        return [JourneyStep.model_validate(step) for step in journey.steps]

    @staticmethod
    def _journey(standard_number: str, category: str) -> list[JourneyStep]:
        return [
            JourneyStep(title="Classify product", status="complete", explanation=category),
            JourneyStep(title="Identify candidate standard", status="complete", explanation=standard_number),
            JourneyStep(title="Check mandatory status", status="attention", explanation="No verified live QCO source is connected", next_action="Verify the current regulatory record"),
            JourneyStep(title="Review product manual", status="pending", explanation="Confirm the current product manual and sampling plan"),
            JourneyStep(title="Arrange recognised testing", status="pending", explanation="Confirm exact laboratory recognition scope"),
            JourneyStep(title="Prepare application", status="pending", explanation="Compile technical and manufacturing documentation"),
        ]
