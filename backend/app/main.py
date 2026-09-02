import logging
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .config import settings
from .db_models import SourceRecord, Standard as StandardRecord
from .database import database_is_ready, get_db
from .middleware import StagingSafetyMiddleware
from .repositories import DocumentRepository, LaboratoryRepository, StandardRepository
from .schemas import (
    ComplianceProfile,
    ConversationCreateRequest,
    ConversationMessageRequest,
    ConversationResponse,
    Document,
    JourneyStep,
    Laboratory,
    LabSearchRequest,
    ProductAnalyseRequest,
    QueryRequest,
    QueryResponse,
    Standard,
    StandardRelationship,
)
from .serializers import document_to_schema, recognitions_to_laboratories, relationship_to_schema, standard_to_schema
from .services.compliance import ComplianceService
from .services.conversations import ConversationService
from .services.retrieval import RetrievalService

logging.basicConfig(level=logging.INFO, format='{"level":"%(levelname)s","event":"%(message)s"}')
logger = logging.getLogger("manakai")

app = FastAPI(
    title="ManakAI API",
    version="0.4.0",
    description="Database-backed Indian Standards and BIS compliance intelligence prototype",
)
app.add_middleware(StagingSafetyMiddleware, config=settings)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Request-ID"],
)


@app.get("/health")
def health():
    return {"status": "ok", "app_env": settings.app_env, "demo_mode": settings.demo_mode, "llm_provider": settings.llm_provider, "llm_model": settings.llm_model or None}


@app.get("/ready")
def ready(session: Session = Depends(get_db)):
    try:
        database_is_ready(session)
        revision = session.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        if revision != settings.expected_schema_revision:
            raise RuntimeError("Database migration revision is not current")
        authoritative_records = session.scalar(select(func.count()).select_from(SourceRecord).where(SourceRecord.verification_status == "AUTHORITATIVE")) or 0
        kettle_standard = session.get(StandardRecord, "is-302-2-15-auth")
        if not settings.demo_mode and (authoritative_records == 0 or kettle_standard is None):
            raise RuntimeError("Required authoritative kettle data is unavailable")
    except Exception as exc:
        logger.exception("readiness_failed")
        raise HTTPException(status_code=503, detail="Service is not ready") from exc
    return {"status": "ready", "database": "ready", "schema_revision": revision, "authoritative_records": authoritative_records}


@app.get("/api/v1/standards", response_model=list[Standard])
def list_standards(q: str = Query(default=""), session: Session = Depends(get_db)):
    repository = StandardRepository(session)
    records = repository.search(q) if q else repository.list()
    expected = "DEMO" if settings.demo_mode else "AUTHORITATIVE"
    return [standard_to_schema(record) for record in records if record.source_kind == expected or (not settings.demo_mode and record.source_kind == "VERIFIED_DERIVED")]


@app.get("/api/v1/standards/{standard_id}", response_model=Standard)
def get_standard(standard_id: str, session: Session = Depends(get_db)):
    standard = StandardRepository(session).get(standard_id)
    if standard is None:
        raise HTTPException(status_code=404, detail="Standard not found")
    return standard_to_schema(standard)


@app.get("/api/v1/standards/{standard_id}/relationships", response_model=list[StandardRelationship])
def get_standard_relationships(standard_id: str, session: Session = Depends(get_db)):
    repository = StandardRepository(session)
    if repository.get(standard_id) is None:
        raise HTTPException(status_code=404, detail="Standard not found")
    return [relationship_to_schema(record) for record in repository.relationships(standard_id)]


@app.post("/api/v1/standards/search", response_model=list[Standard])
def standards_search(request: QueryRequest, session: Session = Depends(get_db)):
    return RetrievalService(session).search_standards(request.query)


@app.post("/api/v1/products/analyse", response_model=ComplianceProfile)
def products_analyse(request: ProductAnalyseRequest, session: Session = Depends(get_db)):
    logger.info("query_received")
    try:
        profile = ComplianceService(session).analyse(request)
    except LookupError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    logger.info("compliance_rule_evaluated")
    return profile


@app.post("/api/v1/compliance/analyse", response_model=ComplianceProfile)
def compliance_analyse(request: ProductAnalyseRequest, session: Session = Depends(get_db)):
    return products_analyse(request, session)


@app.get("/api/v1/compliance/{profile_id}", response_model=ComplianceProfile)
def get_compliance(profile_id: str, session: Session = Depends(get_db)):
    try:
        return ComplianceService(session).get(profile_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/v1/compliance/{profile_id}/journey", response_model=list[JourneyStep])
def get_journey(profile_id: str, session: Session = Depends(get_db)):
    try:
        return ComplianceService(session).journey(profile_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/v1/labs", response_model=list[Laboratory])
def list_labs(as_of_date: date | None = Query(default=None), session: Session = Depends(get_db)):
    repository = LaboratoryRepository(session)
    records = repository.list_recognitions()
    records = [record for record in records if record.source_kind == ("DEMO" if settings.demo_mode else "AUTHORITATIVE")]
    if as_of_date:
        records = [record for record in records if record.status == "RECOGNISED" and (record.valid_from is None or record.valid_from <= as_of_date) and (record.valid_until is None or record.valid_until >= as_of_date)]
    return recognitions_to_laboratories(records)


@app.post("/api/v1/labs/search", response_model=list[Laboratory])
def labs_search(request: LabSearchRequest, session: Session = Depends(get_db)):
    records = LaboratoryRepository(session).search_recognitions(
        query=request.query,
        standard_number=request.standard_number,
        location=request.location,
        as_of_date=request.as_of_date,
    )
    records = [record for record in records if record.source_kind == ("DEMO" if settings.demo_mode else "AUTHORITATIVE")]
    return recognitions_to_laboratories(records)


@app.post("/api/v1/qa", response_model=QueryResponse)
@app.post("/api/v1/query", response_model=QueryResponse)
def query(request: QueryRequest, session: Session = Depends(get_db)):
    logger.info("intent_classified")
    return RetrievalService(session).answer(request.query)


@app.post("/api/v1/conversations", response_model=ConversationResponse)
def create_conversation(request: ConversationCreateRequest, session: Session = Depends(get_db)):
    return ConversationService(session).create(request.language)


@app.get("/api/v1/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, session: Session = Depends(get_db)):
    try:
        return ConversationService(session).get(conversation_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/conversations/{conversation_id}/messages", response_model=ConversationResponse)
def add_conversation_message(conversation_id: str, request: ConversationMessageRequest, session: Session = Depends(get_db)):
    try:
        return ConversationService(session).message(conversation_id, request.message, request.language)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/chat", response_model=ConversationResponse)
def chat(request: ConversationMessageRequest, session: Session = Depends(get_db)):
    service = ConversationService(session)
    conversation = service.create(request.language)
    return service.message(conversation.conversation_id, request.message, request.language)


@app.get("/api/v1/documents/{document_id}", response_model=Document)
def get_document(document_id: str, session: Session = Depends(get_db)):
    document = DocumentRepository(session).get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document_to_schema(document)
