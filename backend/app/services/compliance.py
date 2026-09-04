from __future__ import annotations

import re
from datetime import date

from sqlalchemy.orm import Session

from ..config import settings
from ..repositories import ComplianceRepository, CoverageRepository, DocumentRepository, LaboratoryRepository, ProductRepository, QCORepository, StandardRepository
from ..schemas import ComplianceProfile, CoverageSummary, ExplanationNode, HallmarkingCentre, JourneyStep, ProductAnalyseRequest, ProductProfile, QCOEvidence, RegulatoryRegime
from ..serializers import citation_to_schema, recognitions_to_laboratories, standard_to_schema
from .citations import CitationValidationService
from .rules import QCORecord, evaluate_certification, temporal_status
from .product_catalog import classify_authoritative


class ComplianceService:
    def __init__(self, session: Session):
        self.session = session
        self.standards = StandardRepository(session)
        self.laboratories = LaboratoryRepository(session)
        self.qcos = QCORepository(session)
        self.products = ProductRepository(session)
        self.documents = DocumentRepository(session)
        self.compliance = ComplianceRepository(session)
        self.coverage = CoverageRepository(session)

    @staticmethod
    def classify(description: str, *, authoritative: bool = False) -> dict:
        if authoritative:
            return classify_authoritative(description)
        text = description.casefold()
        if "kettle" in text or "केतली" in text:
            power = re.search(r"(?<!\d)(\d{2,5})\s*(?:w(?:att)?s?|वाट)\b", text)
            power_kw = re.search(r"(?<![\d.])(\d+(?:\.\d+)?)\s*k(?:ilo)?w\b", text)
            voltage = re.search(r"(?<!\d)(\d{2,4})\s*(?:v|volt|volts|वोल्ट)\b", text)
            household = any(term in text for term in ("household", "house use", "domestic", "home", "homes", "ghar", "घरेलू", "घर"))
            commercial = any(term in text for term in ("commercial", "hotel", "restaurant", "व्यावसायिक", "होटल", "रेस्तरां"))
            india = any(term in text for term in ("india", "indian", "भारत", "bis"))
            rated_power = int(power.group(1)) if power else int(float(power_kw.group(1)) * 1000) if power_kw else None
            structured = {
                "product_type": "electric_kettle",
                "category": "appliances_for_heating_liquids",
                "intended_use": "household" if household else "commercial" if commercial else None,
                "rated_power_w": rated_power,
                "country": "India" if india else None,
            }
            if voltage:
                structured["rated_voltage_v"] = int(voltage.group(1))
            attributes = ["Electric kettle", "Appliance for heating liquids"]
            if household: attributes.append("Household use")
            elif commercial: attributes.append("Commercial use")
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
        if authoritative and not classified.get("category_slug"):
            return self._analyse_unsupported(request, classified, as_of)
        if authoritative:
            coverage = self.coverage.for_category(classified["category_slug"])
            if coverage is None and classified["category_slug"] == "appliances-for-heating-liquids":
                # Backwards-compatible for callers that run the original kettle-only
                # ingestion target rather than the Phase 2E aggregate target.
                from ..ingestion.verticals import ensure_kettle_coverage
                ensure_kettle_coverage(self.session)
                self.session.flush()
                coverage = self.coverage.for_category(classified["category_slug"])
            if coverage is None:
                return self._analyse_unsupported(request, {**classified, "unsupported": True}, as_of)
            standard = coverage.primary_standard
            if standard is None:
                return self._analyse_unsupported(request, {**classified, "unsupported": True}, as_of)
            return self._analyse_authoritative(request, classified, standard, as_of, coverage)
        standard = self.standards.get(classified["standard_id"])
        if standard is None:
            message = "Authoritative kettle data has not been ingested" if authoritative else "Seeded candidate standard is missing"
            raise LookupError(message)
        return self._analyse_demo(request, classified, standard, as_of)

    def _analyse_unsupported(self, request, classified, as_of):
        ambiguous = bool(classified.get("ambiguous"))
        candidates = classified.get("structured", {}).get("candidate_categories", [])
        reason = "The product description is ambiguous; choose the intended helmet use before a standard is selected." if ambiguous else "This product family has not yet been verified in ManakAI's authoritative coverage registry."
        warnings = [reason]
        if candidates:
            warnings.append("Candidate categories: " + ", ".join(candidates) + ".")
        product_profile = self.products.create_profile(
            name=request.description.strip(), category=classified["category"], role=request.role, description=request.description.strip(),
            language=request.language, attributes=classified["attributes"], missing_attributes=classified["missing"],
            structured_attributes={k: v for k, v in classified["structured"].items() if k != "candidate_categories"}, source_kind="AUTHORITATIVE",
        )
        profile = self.compliance.create(
            product_profile_id=product_profile.id, standard_id=None, confidence=classified["confidence"], mandatory_status="NOT_EVALUATED",
            qco_id=None, certification_scheme_id=None, tests=[], required_documents=[], warnings=warnings,
            journey_steps=[JourneyStep(title="Product coverage checked", status="attention", explanation=reason, next_action="Refine the product description or request a new authoritative vertical").model_dump()],
            as_of_date=as_of, data_mode="AUTHORITATIVE", explanation_tree={"coverage_status": "UNSUPPORTED", "coverage_reason": reason, "candidate_categories": candidates},
        )
        self.session.commit()
        return self.get(profile.id)

    def _analyse_authoritative(self, request, classified, standard, as_of, coverage):
        resolved = self.qcos.resolve(
            standard_id=standard.id,
            product_category=coverage.product_category.slug,
            enterprise_category=request.enterprise_category,
            as_of_date=as_of,
        )
        if not resolved and request.enterprise_category != "GENERAL":
            resolved = self.qcos.resolve(standard_id=standard.id, product_category=coverage.product_category.slug, enterprise_category="GENERAL", as_of_date=as_of)
        qco, applicability = resolved if resolved else (None, None)
        successor = self.session.get(type(qco), qco.superseded_by_id) if qco and qco.superseded_by_id else None
        superseded_on_date = bool(successor and successor.notification_date and successor.notification_date <= as_of)
        stored_status = qco.status if superseded_on_date or qco.status not in {"SUPERSEDED", "WITHDRAWN"} else "ACTIVE"
        record = QCORecord(
            standard.number,
            applicability.effective_from if applicability else None,
            stored_status if qco else "UNKNOWN",
            bool(qco and qco.source_verified),
            qco.notification_date if qco else None,
            applicability.effective_until if applicability else None,
            superseded_on_date,
        ) if qco else None
        regulatory_status = temporal_status(record, as_of) if record else "UNKNOWN"
        mandatory_status = evaluate_certification(record, as_of)
        scheme = self.standards.scheme_for_qco(qco.id) if qco else None
        tests = [item.name for item in self.standards.tests_for(standard.id)]
        warnings = []
        if classified["structured"].get("product_type") == "electric_kettle" and not classified["structured"].get("rated_power_w"):
            warnings.append("Rated power was not supplied; model grouping implications cannot be evaluated.")
        if classified["structured"].get("product_type") == "electric_kettle" and not classified["structured"].get("rated_voltage_v"):
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
            {"question": "Why was this product classified here?", "conclusion": f"{classified['attributes'][0] if classified['attributes'] else request.description} → {coverage.product_category.name}", "facts": [
                {"label": "Product category", "value": coverage.product_category.name}, {"label": "Coverage", "value": coverage.coverage_status},
            ]},
            {"question": "Why was this standard selected?", "conclusion": f"{standard.number}:{standard.version}", "facts": [
                {"label": "Mapped category", "value": coverage.product_category.name}, {"label": "Specific standard", "value": f"{standard.number}:{standard.version}"},
            ]},
            {"question": "Why this regulatory status?", "conclusion": regulatory_status, "facts": [
                {"label": "QCO", "value": qco.notification_number if qco else None}, {"label": "Enterprise category", "value": request.enterprise_category},
                {"label": "Implementation date", "value": effective.isoformat() if effective else None}, {"label": "Query date", "value": as_of.isoformat()},
            ]},
        ]
        journey = self._regime_journey(coverage, standard, regulatory_status, scheme is not None, bool(tests))
        warnings.extend(list(coverage.known_limitations or []))
        metadata = coverage.metadata_json or {}
        profile = self.compliance.create(
            product_profile_id=product_profile.id, standard_id=standard.id, additional_standard_ids=[item.target_standard_id for item in self.standards.relationships(standard.id)],
            confidence=classified["confidence"], mandatory_status=mandatory_status, qco_id=qco.id if qco else None,
            certification_scheme_id=scheme.id if scheme else None, tests=tests,
            required_documents=list(metadata.get("required_documents", [])),
            warnings=warnings, journey_steps=[item.model_dump() for item in journey], as_of_date=as_of,
            data_mode="AUTHORITATIVE", explanation_tree={"nodes": explanation, "enterprise_category": request.enterprise_category, "effective_from": effective.isoformat() if effective else None}, coverage_id=coverage.id, regime_id=coverage.regime_id,
        )
        evidence_specs = metadata.get("evidence", [])
        if coverage.id == "coverage-electric-kettle":
            evidence_specs = [("doc-bis-kettle-guide", "chunk-bis-kettle-guide", "BIS identifies electric kettles as appliances for heating liquids"), ("doc-qco-household-appliances-2026", "chunk-qco-household-appliances-2026", "QCO lists appliances for heating liquids and implementation dates"), ("doc-pm-is-302-2-15-2024", "chunk-kettle-manual-1", "IS 302-2-15:2009 appliances for heating liquids")]
        elif coverage.regime and coverage.regime.regime_type == "HALLMARKING":
            evidence_specs = [("doc-hallmarking-verify-huid", "chunk-hallmarking-verify-huid", "HUID verification is performed through the official BIS Care app"), ("doc-hallmarking-identify-hallmark", "chunk-hallmarking-identify-hallmark", "BIS hallmark elements")]
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
        standards.sort(key=lambda item: (item.id != (profile.coverage.primary_standard_id if profile.coverage else ""), item.number))
        lab_standard = self.standards.get(profile.coverage.primary_standard_id) if profile.coverage and profile.coverage.primary_standard_id else (standards[0] if standards else None)
        recognitions = self.laboratories.for_standard(lab_standard.id, profile.as_of_date) if lab_standard else []
        citations = [item for item in self.documents.citations_for_profile(profile_id) if item.validation_status != "INVALID"]
        journey = self.compliance.journey(profile_id)
        product_profile = profile.product_profile
        qco_schema = None
        if profile.qco:
            enterprise = (profile.explanation_tree or {}).get("enterprise_category", "GENERAL")
            effective = (profile.explanation_tree or {}).get("effective_from")
            successor = self.session.get(type(profile.qco), profile.qco.superseded_by_id) if profile.qco.superseded_by_id else None
            superseded_on_date = bool(successor and successor.notification_date and successor.notification_date <= (profile.as_of_date or date.today()))
            stored_status = profile.qco.status if superseded_on_date or profile.qco.status not in {"SUPERSEDED", "WITHDRAWN"} else "ACTIVE"
            qco_record = QCORecord(lab_standard.number if lab_standard else "", date.fromisoformat(effective) if effective else profile.qco.effective_date, stored_status, profile.qco.source_verified, profile.qco.notification_date, profile.qco.effective_until, superseded_on_date)
            qco_schema = QCOEvidence(id=profile.qco.id, title=profile.qco.title, notification_number=profile.qco.notification_number, notification_date=profile.qco.notification_date, effective_from=qco_record.effective_date, status=temporal_status(qco_record, profile.as_of_date or date.today()), enterprise_category=enterprise, source_url=profile.qco.source_url, source_kind=profile.qco.source_kind)
        coverage_schema = self._coverage_schema(profile.coverage, fallback={**(profile.explanation_tree or {}), "_demo": profile.data_mode == "DEMO"})
        hallmarking_centres = []
        consumer_actions = []
        if profile.regime and profile.regime.regime_type == "HALLMARKING":
            hallmarking_centres = [HallmarkingCentre.model_validate(item) for item in self.coverage.hallmarking_centres(as_of_date=profile.as_of_date)]
            consumer_actions = [step for guide in self.coverage.hallmarking_guidance() for step in (guide.guidance or [])]
        return ComplianceProfile(
            id=profile.id,
            product=ProductProfile(interpreted_product=product_profile.input_description or product_profile.product.name, role=product_profile.role, category=product_profile.product.category or "Unclassified", attributes=list(product_profile.attributes or []), missing_attributes=list(product_profile.missing_attributes or []), structured_attributes=dict(product_profile.structured_attributes or {})),
            applicable_standards=[standard_to_schema(item) for item in standards], mandatory_status=profile.mandatory_status,
            qco=qco_schema, certification_scheme=profile.certification_scheme.name if profile.certification_scheme else None,
            tests=list(profile.tests or []), required_documents=list(profile.required_documents or []), laboratories=recognitions_to_laboratories(recognitions),
            next_steps=[JourneyStep.model_validate(step) for step in (journey.steps if journey else [])], evidence=[citation_to_schema(item) for item in citations],
            confidence=profile.confidence, warnings=list(profile.warnings or []), as_of_date=profile.as_of_date or date.today(), data_mode=profile.data_mode,
            explanation=[ExplanationNode.model_validate(item) for item in (profile.explanation_tree or {}).get("nodes", [])],
            coverage=coverage_schema,
            regulatory_regime=RegulatoryRegime.model_validate(profile.regime) if profile.regime else None,
            hallmarking_centres=hallmarking_centres,
            consumer_actions=consumer_actions,
        )

    @staticmethod
    def _coverage_schema(coverage, fallback: dict | None = None) -> CoverageSummary:
        if coverage:
            return CoverageSummary(
                id=coverage.id, category_slug=coverage.product_category.slug, category_name=coverage.product_category.name,
                primary_standard=f"{coverage.primary_standard.number}:{coverage.primary_standard.version}" if coverage.primary_standard else None,
                coverage_status=coverage.coverage_status, coverage_reason=coverage.coverage_reason, verified_at=coverage.verified_at,
                authoritative_sources_count=coverage.authoritative_sources_count, known_limitations=list(coverage.known_limitations or []),
                standard_metadata_available=coverage.standard_metadata_available, compliance_verified=coverage.compliance_verified,
                regulatory_regime=RegulatoryRegime.model_validate(coverage.regime) if coverage.regime else None,
            )
        fallback = fallback or {}
        if fallback.get("_demo"):
            return CoverageSummary(id="demo", category_slug="demo", category_name="Deterministic demonstration data", coverage_status="METADATA_ONLY", coverage_reason="This profile uses labelled synthetic DEMO data and is not authoritative BIS coverage.", known_limitations=["Verify every regulatory fact against current official sources."], standard_metadata_available=True, compliance_verified=False)
        return CoverageSummary(id="unsupported", category_slug="unsupported", category_name="Unsupported or ambiguous product", coverage_status="UNSUPPORTED", coverage_reason=fallback.get("coverage_reason", "No authoritative coverage record"), known_limitations=[], standard_metadata_available=False, compliance_verified=False)

    @staticmethod
    def _regime_journey(coverage, standard, regulatory_status: str, has_scheme: bool, has_tests: bool) -> list[JourneyStep]:
        if coverage.regime and coverage.regime.regime_type == "HALLMARKING":
            return [
                JourneyStep(title="Article classified", status="complete", explanation=coverage.product_category.name),
                JourneyStep(title="Fineness standard identified", status="complete", explanation=f"{standard.number}:{standard.version}"),
                JourneyStep(title="Mandatory hallmarking order checked", status="complete", explanation=f"Date-aware result: {regulatory_status}"),
                JourneyStep(title="Hallmark elements reviewed", status="complete", explanation="BIS mark, purity/fineness and six-digit HUID"),
                JourneyStep(title="HUID verification", status="attention", explanation="Use Verify HUID in the official BIS Care app; ManakAI does not perform verification."),
                JourneyStep(title="Assaying and Hallmarking Centre", status="pending", explanation="Use the official BIS AHC directory and confirm current recognition."),
            ]
        manual = (coverage.metadata_json or {}).get("manual_id", "current BIS product manual")
        return [
            JourneyStep(title="Product classified", status="complete", explanation=coverage.product_category.name),
            JourneyStep(title="Applicable standard identified", status="complete", explanation=f"{standard.number}:{standard.version}"),
            JourneyStep(title="QCO status checked", status="attention" if regulatory_status in {"UPCOMING", "UNKNOWN"} else "complete", explanation=f"Date-aware result: {regulatory_status}"),
            JourneyStep(title="Certification scheme identified", status="complete" if has_scheme else "attention", explanation="Scheme I (ISI Mark Scheme)" if has_scheme else "No verified scheme relationship"),
            JourneyStep(title="Product manual identified", status="complete", explanation=manual),
            JourneyStep(title="Testing requirements reviewed", status="complete" if has_tests else "attention", explanation="Clause-level test headings from captured official evidence"),
            JourneyStep(title="Recognised laboratory search", status="pending", explanation="Recognition is filtered by scope and query date"),
            JourneyStep(title="Documentation preparation", status="pending", explanation="Prepare the declarations listed in the current product manual"),
        ]

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
