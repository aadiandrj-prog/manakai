from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SourceKind(str, Enum):
    AUTHORITATIVE = "AUTHORITATIVE"
    VERIFIED_DERIVED = "VERIFIED_DERIVED"
    DEMO = "DEMO"
    UNVERIFIED = "UNVERIFIED"


class RegulatoryStatus(str, Enum):
    DRAFT = "DRAFT"
    NOTIFIED = "NOTIFIED"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    UPCOMING = "UPCOMING"
    WITHDRAWN = "WITHDRAWN"
    AMENDED = "AMENDED"
    UNKNOWN = "UNKNOWN"


class CoverageStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIAL = "PARTIAL"
    METADATA_ONLY = "METADATA_ONLY"
    UNSUPPORTED = "UNSUPPORTED"


class RegulatoryRegimeType(str, Enum):
    PRODUCT_CERTIFICATION = "PRODUCT_CERTIFICATION"
    HALLMARKING = "HALLMARKING"
    UNKNOWN = "UNKNOWN"


class Intent(str, Enum):
    PRODUCT_COMPLIANCE = "PRODUCT_COMPLIANCE"
    STANDARD_QA = "STANDARD_QA"
    CERTIFICATION_QUERY = "CERTIFICATION_QUERY"
    LAB_SEARCH = "LAB_SEARCH"
    CONSUMER_QUERY = "CONSUMER_QUERY"
    HALLMARKING_QUERY = "HALLMARKING_QUERY"
    GENERAL_BIS_QUERY = "GENERAL_BIS_QUERY"
    UNKNOWN = "UNKNOWN"


class SupportedLanguage(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    HINGLISH = "hinglish"


class Citation(APIModel):
    id: str
    document_title: str
    document_type: str
    standard_number: str | None = None
    version: str | None = None
    page: int | None = None
    clause: str | None = None
    source_url: str | None = None
    publication_date: date | None = None
    effective_date: date | None = None
    retrieved_at: datetime | None = None
    source_kind: SourceKind = SourceKind.DEMO
    source_authority: str | None = None
    document_identifier: str | None = None
    status: RegulatoryStatus = RegulatoryStatus.UNKNOWN
    verification_status: str = "UNVERIFIED"
    claim: str | None = None
    validation_status: str = "PENDING"


class Standard(APIModel):
    id: str
    number: str
    title: str
    version: str
    status: RegulatoryStatus
    category: str
    scope: str
    publication_date: date | None = None
    effective_date: date | None = None
    retrieved_at: datetime | None = None
    source_kind: SourceKind = SourceKind.DEMO


class StandardRelationship(APIModel):
    id: str
    relationship_type: str
    source_standard_id: str
    target_standard: Standard


class Laboratory(APIModel):
    id: str
    name: str
    city: str | None = None
    state: str | None = None
    address: str | None = None
    standards: list[str]
    capabilities: list[str]
    source_kind: SourceKind = SourceKind.DEMO
    scope_identifier: str | None = None
    scope: str | None = None
    test_clauses: list[str] = []
    valid_from: date | None = None
    valid_until: date | None = None
    recognition_status: str = "UNKNOWN"
    source_url: str | None = None
    retrieved_at: datetime | None = None
    warning: str | None = None
    grade_type: str | None = None
    testing_charge: str | None = None
    remark: str | None = None


class Document(APIModel):
    id: str
    title: str
    document_type: str
    standard_id: str | None = None
    standard_number: str | None = None
    version: str | None = None
    source_url: str | None = None
    publication_date: date | None = None
    effective_date: date | None = None
    retrieved_at: datetime | None = None
    source_kind: SourceKind = SourceKind.DEMO


class ProductAnalyseRequest(APIModel):
    description: str = Field(min_length=3, max_length=2000)
    role: str = "manufacturer"
    language: str = "en"
    as_of_date: date | None = None
    enterprise_category: str = Field(default="GENERAL", pattern="^(GENERAL|SMALL|MICRO)$")


class IntentClassification(APIModel):
    intent: Intent
    confidence: float = Field(ge=0, le=1)
    route_reason: str


class ProductExtraction(APIModel):
    product_type: str | None = None
    category: str | None = None
    actor: str | None = None
    intended_use: str | None = None
    rated_power_w: int | None = None
    rated_voltage_v: int | None = None
    country: str | None = None
    enterprise_category: str | None = None
    additional_attributes: dict[str, str | int | float | bool | None] = {}
    missing_required_fields: list[str] = []
    candidate_categories: list[str] = []
    confidence: float = Field(default=0, ge=0, le=1)


class ClarificationDecision(APIModel):
    required: bool
    fields: list[str] = []
    question: str | None = None


class ConversationInterpretation(APIModel):
    language: SupportedLanguage
    intent: IntentClassification
    product: ProductExtraction | None = None
    as_of_date: date | None = None
    clarification: ClarificationDecision


class ProductProfile(APIModel):
    interpreted_product: str
    role: str
    category: str
    attributes: list[str]
    missing_attributes: list[str]
    structured_attributes: dict[str, str | int | float | bool | None] = {}


class QCOEvidence(APIModel):
    id: str
    title: str
    notification_number: str | None = None
    notification_date: date | None = None
    effective_from: date | None = None
    status: RegulatoryStatus
    enterprise_category: str
    source_url: str | None = None
    source_kind: SourceKind


class ExplanationNode(APIModel):
    question: str
    conclusion: str
    facts: list[dict[str, str | None]] = []


class JourneyStep(APIModel):
    title: str
    status: str
    explanation: str
    next_action: str | None = None


class RegulatoryRegime(APIModel):
    id: str
    slug: str
    name: str
    regime_type: RegulatoryRegimeType
    description: str


class CoverageSummary(APIModel):
    id: str
    category_slug: str
    category_name: str
    primary_standard: str | None = None
    coverage_status: CoverageStatus
    coverage_reason: str
    verified_at: datetime | None = None
    authoritative_sources_count: int = 0
    known_limitations: list[str] = []
    standard_metadata_available: bool = False
    compliance_verified: bool = False
    regulatory_regime: RegulatoryRegime | None = None


class CoverageStats(APIModel):
    total: int
    verified: int
    partial: int
    metadata_only: int
    unsupported: int
    authoritative_sources: int


class HallmarkingCentre(APIModel):
    id: str
    name: str
    centre_identifier: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    status: str
    valid_from: date | None = None
    valid_until: date | None = None
    scope: str | None = None
    source_url: str
    retrieved_at: datetime
    source_kind: SourceKind
    warning: str | None = None


class HallmarkingGuidance(APIModel):
    id: str
    topic: str
    title: str
    guidance: list[str]
    source_url: str
    source_kind: SourceKind


class ComplianceProfile(APIModel):
    id: str
    product: ProductProfile
    applicable_standards: list[Standard]
    mandatory_status: str
    qco: QCOEvidence | None
    certification_scheme: str | None
    tests: list[str]
    required_documents: list[str]
    laboratories: list[Laboratory]
    next_steps: list[JourneyStep]
    evidence: list[Citation]
    confidence: float = Field(ge=0, le=1)
    warnings: list[str]
    as_of_date: date
    data_mode: SourceKind
    explanation: list[ExplanationNode] = []
    coverage: CoverageSummary
    regulatory_regime: RegulatoryRegime | None = None
    hallmarking_centres: list[HallmarkingCentre] = []
    consumer_actions: list[str] = []


class QueryRequest(APIModel):
    query: str = Field(min_length=2, max_length=2000)
    language: str = "auto"


class QueryResponse(APIModel):
    intent: Intent
    answer: str
    citations: list[Citation]
    confidence: float
    warnings: list[str]


class EvidenceReference(APIModel):
    evidence_id: str
    citation: Citation


class RegulatoryAnswerPackage(APIModel):
    intent: Intent
    language: SupportedLanguage
    product_profile: ProductProfile | None = None
    compliance_result: ComplianceProfile | None = None
    evidence: list[EvidenceReference] = []
    warnings: list[str] = []


class ConversationCreateRequest(APIModel):
    language: str = "auto"


class ConversationMessageRequest(APIModel):
    message: str = Field(min_length=1, max_length=4000)
    language: str = "auto"


class ConversationMessage(APIModel):
    id: str
    role: str
    content: str
    language: SupportedLanguage
    created_at: datetime


class ConversationResponse(APIModel):
    conversation_id: str
    language: SupportedLanguage
    intent: Intent
    answer: str
    clarification_required: bool = False
    unresolved_attributes: list[str] = []
    compliance_profile: ComplianceProfile | None = None
    evidence: list[EvidenceReference] = []
    warnings: list[str] = []
    provider: str = "deterministic"
    used_fallback: bool = True
    messages: list[ConversationMessage] = []


class LabSearchRequest(APIModel):
    query: str = ""
    standard_number: str | None = None
    location: str | None = None
    as_of_date: date | None = None
