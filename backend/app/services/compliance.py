from __future__ import annotations

import re
from datetime import date

from sqlalchemy.orm import Session

from ..config import settings
from ..repositories import ComplianceRepository, DocumentRepository, LaboratoryRepository, ProductRepository, QCORepository, StandardRepository
from ..schemas import ComplianceProfile, ExplanationNode, JourneyStep, ProductAnalyseRequest, ProductProfile, QCOEvidence
from ..serializers import citation_to_schema, recognitions_to_laboratories, standard_to_schema
from .citations import CitationValidationService
from .rules import QCORecord, evaluate_certification, temporal_status


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
    def classify(description: str, *, authoritative: bool = False) -> dict:
        text = description.casefold()
        if "kettle" in text or "केतली" in text:
            power = re.search(r"(?<!\d)(\d{2,5})\s*w(?:att)?s?\b", text)
            power_kw = re.search(r"(?<![\d.])(\d+(?:\.\d+)?)\s*k(?:ilo)?w\b", text)
            voltage = re.search(r"(?<!\d)(\d{2,4})\s*(?:v|volt|volts|वोल्ट)\b", text)
            household = any(term in text for term in ("household", "domestic", "home", "homes", "ghar", "घरेलू", "घर"))
            india = any(term in text for term in ("india", "indian", "भारत", "bis"))
            rated_power = int(power.group(1)) if power else int(float(power_kw.group(1)) * 1000) if power_kw else None
            structured = {
                "product_type": "electric_kettle",
                "category": "appliances_for_heating_liquids",
                "intended_use": "household" if household else None,
                "rated_power_w": rated_power,
                "country": "India" if india else None,
            }
            if voltage:
                structured["rated_voltage_v"] = int(voltage.group(1))
            attributes = ["Electric kettle", "Appliance for heating liquids"]
            if household: attributes.append("Household use")
            if rated_power: attributes.append(f"{rated_power} W rated power")
            if voltage: attributes.append(f"{voltage.group(1)} V rated voltage")
            if india: attributes.append("Market: India")
            return {
                "standard_id": "is-302-2-15-auth" if authoritative else "is-302-2-15",
                "category": "Appliances for Heating Liquids" if authoritative else "Household electrical appliance",
                "attributes": attributes,
                "structured": structured,
                "missing": ["rated voltage"] if not voltage else [],
                "confidence": 0.98 if authoritative else 0.86,
            }
        if "helmet" in text:
            return {"standard_id": "is-4151", "category": "Protective rider equipment", "attributes": ["Head protection", "Two-wheeler use"], "structured": {}, "missing": ["rated voltage", "installation type", "battery chemistry"], "confidence": 0.84}
        if "steel" in text or "rebar" in text:
            return {"standard_id": "is-1786", "category": "Construction reinforcement material", "attributes": ["Deformed bar", "Concrete reinforcement"], "structured": {}, "missing": [], "confidence": 0.82}
        return {"standard_id": "is-10322-5-8", "category": "Electrical lighting equipment", "attributes": ["Portable", "Rechargeable battery", "LED light source", "Emergency use"], "structured": {}, "missing": ["rated voltage", "installation type", "battery chemistry"], "confidence": 0.91}

    def analyse(self, request: ProductAnalyseRequest) -> ComplianceProfile:
        as_of = request.as_of_date or date.today()
        authoritative = not settings.demo_mode
        classified = self.classify(request.description, authoritative=authoritative)
        if authoritative and classified["structured"].get("product_type") != "electric_kettle":
            raise LookupError("AUTHORITATIVE mode currently supports only the electric-kettle vertical")
        standard = self.standards.get(classified["standard_id"])
        if standard is None:
            message = "Authoritative kettle data has not been ingested" if authoritative else "Seeded candidate standard is missing"
            raise LookupError(message)
        if authoritative:
            return self._analyse_authoritative(request, classified, standard, as_of)
        return self._analyse_demo(request, classified, standard, as_of)

    def _analyse_authoritative(self, request, classified, standard, as_of):
        resolved = self.qcos.resolve(
            standard_id=standard.id,
            product_category="appliances-for-heating-liquids",
            enterprise_category=request.enterprise_category,
        )
        qco, applicability = resolved if resolved else (None, None)
        record = QCORecord(
            standard.number,
            applicability.effective_from if applicability else None,
            qco.status if qco else "UNKNOWN",
            bool(qco and qco.source_verified),
            qco.notification_date if qco else None,
            applicability.effective_until if applicability else None,
            bool(qco and qco.superseded_by_id),
        ) if qco else None
        regulatory_status = temporal_status(record, as_of) if record else "UNKNOWN"
        mandatory_status = evaluate_certification(record, as_of)
        scheme = self.standards.scheme_for_qco(qco.id) if qco else None
        tests = [item.name for item in self.standards.tests_for(standard.id)]
        warnings = []
        if not classified["structured"].get("rated_power_w"):
            warnings.append("Rated power was not supplied; model grouping implications cannot be evaluated.")
        if not classified["structured"].get("rated_voltage_v"):
            warnings.append("Rated voltage was not supplied. The QCO voltage scope cannot be conclusively evaluated; confirm whether the appliance is within 250 V single-phase or the other stated voltage limits.")
        if not classified["structured"].get("country"):
            warnings.append("Country was not explicit; this profile assumes the requested regulatory context is India.")
        product_profile = self.products.create_profile(
            name=request.description.strip(), category=classified["category"], role=request.role,
            description=request.description.strip(), language=request.language, attributes=classified["attributes"],
            missing_attributes=classified["missing"], structured_attributes=classified["structured"], source_kind="AUTHORITATIVE",
        )
        effective = applicability.effective_from if applicability else None
        explanation = [
            {"question": "Why was this product classified here?", "conclusion": "Electric kettle → Appliances for Heating Liquids", "facts": [
                {"label": "Product", "value": "Electric kettle"}, {"label": "Category", "value": "Appliances for Heating Liquids"},
                {"label": "Evidence", "value": "Official BIS consumer guide"},
            ]},
            {"question": "Why was this standard selected?", "conclusion": "IS 302 (Part 2/Sec 15):2009", "facts": [
                {"label": "Mapped category", "value": "Appliances for Heating Liquids"}, {"label": "Specific standard", "value": f"{standard.number}:{standard.version}"},
                {"label": "General framework", "value": "IS 302 (Part 1):2024"},
            ]},
            {"question": "Why this regulatory status?", "conclusion": regulatory_status, "facts": [
                {"label": "QCO", "value": qco.notification_number if qco else None}, {"label": "Enterprise category", "value": request.enterprise_category},
                {"label": "Implementation date", "value": effective.isoformat() if effective else None}, {"label": "Query date", "value": as_of.isoformat()},
            ]},
        ]
        journey = self._authoritative_journey(standard.number, regulatory_status, scheme is not None, bool(tests))
        profile = self.compliance.create(
            product_profile_id=product_profile.id, standard_id=standard.id, additional_standard_ids=["is-302-1-2024-auth"],
            confidence=classified["confidence"], mandatory_status=mandatory_status, qco_id=qco.id if qco else None,
            certification_scheme_id=scheme.id if scheme else None, tests=tests,
            required_documents=["Model/type, rating and capacity declaration", "Appliance class and degree of protection", "Material group and pollution degree", "Instruction/operation manual with product photographs"],
            warnings=warnings, journey_steps=[item.model_dump() for item in journey], as_of_date=as_of,
            data_mode="AUTHORITATIVE", explanation_tree={"nodes": explanation, "enterprise_category": request.enterprise_category, "effective_from": effective.isoformat() if effective else None},
        )
        evidence_specs = [
            ("doc-bis-kettle-guide", "chunk-bis-kettle-guide", "BIS identifies electric kettles as appliances for heating liquids"),
            ("doc-qco-household-appliances-2026", "chunk-qco-household-appliances-2026", "QCO lists appliances for heating liquids and implementation dates"),
            ("doc-pm-is-302-2-15-2024", "chunk-kettle-manual-1", "IS 302-2-15:2009 appliances for heating liquids"),
            ("doc-pm-is-302-2-15-2024", "chunk-kettle-manual-5", "Higher input rating model grouping guidance"),
        ]
        validator = CitationValidationService(self.session)
        for document_id, chunk_id, claim in evidence_specs:
            citation = self.compliance.attach_evidence(profile.id, document_id=document_id, chunk_id=chunk_id, claim=claim, source_kind="AUTHORITATIVE")
            result = validator.mark(citation, require_current=True)
            if not result.valid:
                profile.warnings = [*profile.warnings, f"Evidence withheld: {result.error}"]
        self.session.commit()
        return self.get(profile.id)

    def _analyse_demo(self, request, classified, standard, as_of):
        qcos = self.qcos.for_standard(standard.id)
        qco = qcos[0] if qcos else None
        mandatory_status = evaluate_certification(QCORecord(standard.number, qco.effective_date, qco.status, qco.source_verified) if qco else None, as_of)
        tests = [test.name for test in self.standards.tests_for(standard.id)]
        scheme = self.standards.scheme_for(standard.id)
        product_profile = self.products.create_profile(name=request.description.strip(), category=classified["category"], role=request.role, description=request.description.strip(), language=request.language, attributes=classified["attributes"], missing_attributes=classified["missing"], structured_attributes=classified["structured"], source_kind="DEMO")
        journey = self._demo_journey(standard.number, classified["category"])
        profile = self.compliance.create(product_profile_id=product_profile.id, standard_id=standard.id, confidence=classified["confidence"], mandatory_status=mandatory_status, qco_id=qco.id if qco else None, certification_scheme_id=scheme.id if scheme else None, tests=tests or ["Product-specific test mapping unavailable"], required_documents=["Product specification", "Critical component list", "Circuit diagram", "Manufacturing process flow"], warnings=["DEMO_MODE is active.", "Mandatory status and effective dates are not verified."], journey_steps=[step.model_dump() for step in journey], as_of_date=as_of, data_mode="DEMO")
        self.compliance.attach_citations(profile.id, self.documents.search_citations(standard.number))
        self.session.commit()
        return self.get(profile.id)

    def get(self, profile_id: str) -> ComplianceProfile:
        profile = self.compliance.get(profile_id)
        if profile is None:
            raise LookupError("Compliance profile not found")
        standard_ids = self.compliance.standard_ids(profile_id)
        standards = [item for standard_id in standard_ids if (item := self.standards.get(standard_id))]
        standards.sort(key=lambda item: (item.number != "IS 302 (Part 2/Sec 15)", item.number))
        lab_standard = next((item for item in standards if item.number == "IS 302 (Part 2/Sec 15)"), standards[0] if standards else None)
        recognitions = self.laboratories.for_standard(lab_standard.id, profile.as_of_date) if lab_standard else []
        citations = [item for item in self.documents.citations_for_profile(profile_id) if item.validation_status != "INVALID"]
        journey = self.compliance.journey(profile_id)
        product_profile = profile.product_profile
        qco_schema = None
        if profile.qco:
            enterprise = (profile.explanation_tree or {}).get("enterprise_category", "GENERAL")
            effective = (profile.explanation_tree or {}).get("effective_from")
            qco_record = QCORecord(standards[0].number if standards else "", date.fromisoformat(effective) if effective else profile.qco.effective_date, profile.qco.status, profile.qco.source_verified, profile.qco.notification_date, profile.qco.effective_until, bool(profile.qco.superseded_by_id))
            qco_schema = QCOEvidence(id=profile.qco.id, title=profile.qco.title, notification_number=profile.qco.notification_number, notification_date=profile.qco.notification_date, effective_from=qco_record.effective_date, status=temporal_status(qco_record, profile.as_of_date or date.today()), enterprise_category=enterprise, source_url=profile.qco.source_url, source_kind=profile.qco.source_kind)
        return ComplianceProfile(
            id=profile.id,
            product=ProductProfile(interpreted_product=product_profile.input_description or product_profile.product.name, role=product_profile.role, category=product_profile.product.category or "Unclassified", attributes=list(product_profile.attributes or []), missing_attributes=list(product_profile.missing_attributes or []), structured_attributes=dict(product_profile.structured_attributes or {})),
            applicable_standards=[standard_to_schema(item) for item in standards], mandatory_status=profile.mandatory_status,
            qco=qco_schema, certification_scheme=profile.certification_scheme.name if profile.certification_scheme else None,
            tests=list(profile.tests or []), required_documents=list(profile.required_documents or []), laboratories=recognitions_to_laboratories(recognitions),
            next_steps=[JourneyStep.model_validate(step) for step in (journey.steps if journey else [])], evidence=[citation_to_schema(item) for item in citations],
            confidence=profile.confidence, warnings=list(profile.warnings or []), as_of_date=profile.as_of_date or date.today(), data_mode=profile.data_mode,
            explanation=[ExplanationNode.model_validate(item) for item in (profile.explanation_tree or {}).get("nodes", [])],
        )

    def journey(self, profile_id: str) -> list[JourneyStep]:
        journey = self.compliance.journey(profile_id)
        if journey is None:
            raise LookupError("Compliance journey not found")
        return [JourneyStep.model_validate(step) for step in journey.steps]

    @staticmethod
    def _authoritative_journey(standard_number: str, regulatory_status: str, has_scheme: bool, has_tests: bool) -> list[JourneyStep]:
        return [
            JourneyStep(title="Product classified", status="complete", explanation="Electric kettle → Appliances for Heating Liquids"),
            JourneyStep(title="Applicable standards identified", status="complete", explanation=f"{standard_number}:2009 with IS 302 (Part 1):2024 general framework"),
            JourneyStep(title="QCO status checked", status="attention" if regulatory_status == "UPCOMING" else "complete", explanation=f"Date-aware result: {regulatory_status}"),
            JourneyStep(title="Certification scheme identified", status="complete" if has_scheme else "attention", explanation="Scheme I (ISI Mark Scheme)" if has_scheme else "No verified scheme relationship"),
            JourneyStep(title="Product manual identified", status="complete", explanation="PM/IS 302-2-15/1/February 2024"),
            JourneyStep(title="Testing requirements reviewed", status="complete" if has_tests else "attention", explanation="Clause-level test headings sourced from BIS LIMS"),
            JourneyStep(title="Recognised laboratory search", status="pending", explanation="Filter BIS LIMS recognition by the intended test date"),
            JourneyStep(title="Documentation preparation", status="pending", explanation="Prepare model, rating, construction and instruction declarations from the product manual"),
        ]

    @staticmethod
    def _demo_journey(standard_number: str, category: str) -> list[JourneyStep]:
        return [JourneyStep(title="Classify product", status="complete", explanation=category), JourneyStep(title="Identify candidate standard", status="complete", explanation=standard_number), JourneyStep(title="Check mandatory status", status="attention", explanation="No verified live QCO source is connected", next_action="Verify the current regulatory record"), JourneyStep(title="Review product manual", status="pending", explanation="Confirm the current product manual and sampling plan"), JourneyStep(title="Arrange recognised testing", status="pending", explanation="Confirm exact laboratory recognition scope"), JourneyStep(title="Prepare application", status="pending", explanation="Compile technical and manufacturing documentation")]
