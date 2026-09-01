import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .fixtures import CITATIONS, LABORATORIES, STANDARDS
from .schemas import LabSearchRequest, ProductAnalyseRequest, QueryRequest, QueryResponse
from .services.compliance import analyse_product
from .services.intent import classify_intent
from .services.retrieval import retrieve_citations, search_standards

logging.basicConfig(level=logging.INFO, format='{"level":"%(levelname)s","event":"%(message)s"}')
logger = logging.getLogger("manakai")

app = FastAPI(title="ManakAI API", version="0.1.0", description="Evidence-first Indian Standards and BIS compliance intelligence prototype")
app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


@app.get("/health")
async def health():
    return {"status": "ok", "demo_mode": settings.demo_mode, "llm_provider": settings.llm_provider}


@app.post("/api/v1/products/analyse")
async def products_analyse(request: ProductAnalyseRequest):
    logger.info("query_received")
    profile = analyse_product(request)
    logger.info("compliance_rule_evaluated")
    return profile


@app.post("/api/v1/compliance/analyse")
async def compliance_analyse(request: ProductAnalyseRequest):
    return analyse_product(request)


@app.get("/api/v1/compliance/{profile_id}")
async def get_compliance(profile_id: str):
    if profile_id != "demo-emergency-lamp":
        raise HTTPException(status_code=404, detail="Compliance profile not found")
    return analyse_product(ProductAnalyseRequest(description="portable rechargeable LED emergency lamp"))


@app.get("/api/v1/compliance/{profile_id}/journey")
async def get_journey(profile_id: str):
    return (await get_compliance(profile_id)).next_steps


@app.get("/api/v1/standards")
async def list_standards(q: str = Query(default="")):
    return search_standards(q) if q else STANDARDS


@app.get("/api/v1/standards/{standard_id}")
async def get_standard(standard_id: str):
    standard = next((item for item in STANDARDS if item.id == standard_id), None)
    if standard is None:
        raise HTTPException(status_code=404, detail="Standard not found")
    return standard


@app.post("/api/v1/standards/search")
async def standards_search(request: QueryRequest):
    return search_standards(request.query)


@app.post("/api/v1/labs/search")
async def labs_search(request: LabSearchRequest):
    query = f"{request.query} {request.location or ''}".casefold()
    return [lab for lab in LABORATORIES if (not request.standard_number or request.standard_number in lab.standards) and (not query.strip() or query.strip() in f"{lab.name} {lab.city} {lab.state} {' '.join(lab.capabilities)}".casefold())]


@app.get("/api/v1/labs")
async def list_labs():
    return LABORATORIES


@app.post("/api/v1/qa", response_model=QueryResponse)
@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    intent = classify_intent(request.query)
    citations = retrieve_citations(request.query)
    logger.info("intent_classified")
    if citations:
        answer = "The demo corpus contains relevant structured metadata, but no authoritative clause text is connected. I can explain the workflow while keeping the legal claim unverified."
    else:
        answer = "I could not verify this requirement from the available authorised BIS sources."
    return QueryResponse(intent=intent, answer=answer, citations=citations, confidence=0.62 if citations else 0.0, warnings=["DEMO_MODE is active", "Verify against current official sources"])


@app.get("/api/v1/citations/{citation_id}")
async def get_citation(citation_id: str):
    citation = next((item for item in CITATIONS if item.id == citation_id), None)
    if citation is None:
        raise HTTPException(status_code=404, detail="Citation not found")
    return citation
