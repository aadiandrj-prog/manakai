from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SourceKind(str, Enum):
    VERIFIED = "verified"
    DEMO = "demo"
    UNVERIFIED = "unverified"


class RegulatoryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    UPCOMING = "UPCOMING"
    WITHDRAWN = "WITHDRAWN"
    AMENDED = "AMENDED"


class Intent(str, Enum):
    PRODUCT_COMPLIANCE = "PRODUCT_COMPLIANCE"
    STANDARD_QA = "STANDARD_QA"
    CERTIFICATION_QUERY = "CERTIFICATION_QUERY"
    LAB_SEARCH = "LAB_SEARCH"
    CONSUMER_QUERY = "CONSUMER_QUERY"
    HALLMARKING_QUERY = "HALLMARKING_QUERY"
    GENERAL_BIS_QUERY = "GENERAL_BIS_QUERY"


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


class ProductProfile(APIModel):
    interpreted_product: str
    role: str
    category: str
    attributes: list[str]
    missing_attributes: list[str]


class JourneyStep(APIModel):
    title: str
    status: str
    explanation: str
    next_action: str | None = None


class ComplianceProfile(APIModel):
    id: str
    product: ProductProfile
    applicable_standards: list[Standard]
    mandatory_status: str
    qco: str | None
    certification_scheme: str | None
    tests: list[str]
    required_documents: list[str]
    laboratories: list[Laboratory]
    next_steps: list[JourneyStep]
    evidence: list[Citation]
    confidence: float = Field(ge=0, le=1)
    warnings: list[str]


class QueryRequest(APIModel):
    query: str = Field(min_length=2, max_length=2000)
    language: str = "auto"


class QueryResponse(APIModel):
    intent: Intent
    answer: str
    citations: list[Citation]
    confidence: float
    warnings: list[str]


class LabSearchRequest(APIModel):
    query: str = ""
    standard_number: str | None = None
    location: str | None = None
