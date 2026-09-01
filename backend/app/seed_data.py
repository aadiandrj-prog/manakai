"""Canonical DEMO_MODE seed records.

Every regulatory record is explicitly marked ``demo``. These records exist to
exercise the full database path and are not authoritative BIS data.
"""
from datetime import datetime, timezone


RETRIEVED_AT = datetime(2026, 9, 1, tzinfo=timezone.utc)

STANDARDS = [
    {"id": "is-10322-5-8", "number": "IS 10322 (Part 5/Sec 8)", "title": "Luminaires — Particular requirements: emergency lighting", "version": "2013", "status": "ACTIVE", "category": "Electrical", "scope": "Demo scope record for luminaires used for emergency lighting. Confirm the current edition, amendments and applicability in the official BIS catalogue.", "source_kind": "DEMO", "retrieved_at": RETRIEVED_AT},
    {"id": "is-302-2-15", "number": "IS 302 (Part 2/Sec 15)", "title": "Safety of household electrical appliances — Appliances for heating liquids", "version": "2009", "status": "AMENDED", "category": "Electrical", "scope": "Demo scope record for household appliances used to heat liquids, including kettle-like products.", "source_kind": "DEMO", "retrieved_at": RETRIEVED_AT},
    {"id": "is-4151", "number": "IS 4151", "title": "Protective helmets for scooter and motorcycle riders", "version": "2015", "status": "ACTIVE", "category": "Consumer safety", "scope": "Demo record representing performance and construction requirements for protective rider helmets.", "source_kind": "DEMO", "retrieved_at": RETRIEVED_AT},
    {"id": "is-1786", "number": "IS 1786", "title": "High strength deformed steel bars and wires for concrete reinforcement", "version": "2008", "status": "AMENDED", "category": "Construction", "scope": "Demo record for reinforcement steel grades, mechanical properties and testing.", "source_kind": "DEMO", "retrieved_at": RETRIEVED_AT},
    {"id": "is-1417", "number": "IS 1417", "title": "Gold and gold alloys, jewellery/artefacts — fineness and marking", "version": "2016", "status": "ACTIVE", "category": "Hallmarking", "scope": "Demo consumer-support record for fineness and marking concepts used in hallmarking guidance.", "source_kind": "DEMO", "retrieved_at": RETRIEVED_AT},
]

STANDARD_RELATIONSHIPS = [
    {"id": "rel-lighting-heating", "source_standard_id": "is-10322-5-8", "target_standard_id": "is-302-2-15", "relationship_type": "RELATED_TO"},
    {"id": "rel-hallmark-consumer", "source_standard_id": "is-1417", "target_standard_id": "is-4151", "relationship_type": "RELATED_TO"},
]

DOCUMENTS = [
    {"id": "doc-emergency-scope", "title": "Emergency lighting standard metadata", "document_type": "Indian Standard metadata", "standard_id": "is-10322-5-8", "version": "2013", "source_kind": "DEMO", "retrieved_at": RETRIEVED_AT},
    {"id": "doc-emergency-manual", "title": "Emergency luminaire product manual mapping", "document_type": "Demo product manual", "standard_id": "is-10322-5-8", "version": "demo-1", "source_kind": "DEMO", "retrieved_at": RETRIEVED_AT},
    {"id": "doc-huid-guide", "title": "Hallmarking consumer guidance fixture", "document_type": "Consumer guidance", "standard_id": "is-1417", "version": "demo-1", "source_kind": "DEMO", "retrieved_at": RETRIEVED_AT},
]

DOCUMENT_CHUNKS = [
    {"id": "chunk-emergency-scope", "document_id": "doc-emergency-scope", "page": None, "clause": None, "section": "Scope metadata", "text": "Demo metadata associates emergency-lighting luminaires with this candidate standard.", "embedding": None},
    {"id": "chunk-emergency-tests", "document_id": "doc-emergency-manual", "page": None, "clause": None, "section": "Testing pathway", "text": "Demo pathway includes construction, insulation, electric strength, endurance and photometry checks.", "embedding": None},
    {"id": "chunk-huid-guide", "document_id": "doc-huid-guide", "page": None, "clause": None, "section": "Consumer verification", "text": "Use an official BIS consumer service to verify a HUID; this fixture does not perform a live verification.", "embedding": None},
]

QCOS = [
    {"id": "qco-lighting-demo", "title": "Emergency lighting QCO placeholder", "status": "ACTIVE", "source_verified": False, "source_kind": "DEMO"},
]

STANDARD_QCOS = [{"id": "standard-qco-lighting", "standard_id": "is-10322-5-8", "qco_id": "qco-lighting-demo"}]

CERTIFICATION_SCHEMES = [
    {"id": "scheme-lighting-demo", "standard_id": "is-10322-5-8", "name": "Demo certification pathway — verify with BIS", "description": "A non-authoritative scheme placeholder used to exercise the compliance journey.", "source_kind": "DEMO"},
]

TESTS = [
    {"id": "test-marking", "standard_id": "is-10322-5-8", "name": "Marking and construction review", "source_kind": "DEMO"},
    {"id": "test-insulation", "standard_id": "is-10322-5-8", "name": "Insulation resistance", "source_kind": "DEMO"},
    {"id": "test-electric-strength", "standard_id": "is-10322-5-8", "name": "Electric strength", "source_kind": "DEMO"},
    {"id": "test-endurance", "standard_id": "is-10322-5-8", "name": "Battery endurance", "source_kind": "DEMO"},
    {"id": "test-photometry", "standard_id": "is-10322-5-8", "name": "Emergency-mode photometry", "source_kind": "DEMO"},
    {"id": "test-kettle-safety", "standard_id": "is-302-2-15", "name": "Electrical safety and heating performance", "source_kind": "DEMO"},
    {"id": "test-helmet-impact", "standard_id": "is-4151", "name": "Impact and retention system testing", "source_kind": "DEMO"},
]

LABORATORIES = [
    {"id": "lab-delhi", "name": "Northstar Electrical Test Lab", "city": "New Delhi", "state": "Delhi", "address": "Synthetic demo address", "source_kind": "DEMO"},
    {"id": "lab-noida", "name": "Apex Product Assurance Centre", "city": "Noida", "state": "Uttar Pradesh", "address": "Synthetic demo address", "source_kind": "DEMO"},
    {"id": "lab-mumbai", "name": "Western Materials Validation Lab", "city": "Mumbai", "state": "Maharashtra", "address": "Synthetic demo address", "source_kind": "DEMO"},
    {"id": "lab-jaipur", "name": "Aravali Assaying Demo Centre", "city": "Jaipur", "state": "Rajasthan", "address": "Synthetic demo address", "source_kind": "DEMO"},
]

LABORATORY_RECOGNITIONS = [
    {"id": "rec-delhi-lighting", "laboratory_id": "lab-delhi", "standard_id": "is-10322-5-8", "capabilities": ["Electrical safety", "Insulation resistance", "Endurance"], "source_kind": "DEMO"},
    {"id": "rec-delhi-kettle", "laboratory_id": "lab-delhi", "standard_id": "is-302-2-15", "capabilities": ["Electrical safety", "Heating performance"], "source_kind": "DEMO"},
    {"id": "rec-noida-lighting", "laboratory_id": "lab-noida", "standard_id": "is-10322-5-8", "capabilities": ["Photometry", "Thermal testing"], "source_kind": "DEMO"},
    {"id": "rec-noida-helmet", "laboratory_id": "lab-noida", "standard_id": "is-4151", "capabilities": ["Impact testing", "Retention system"], "source_kind": "DEMO"},
    {"id": "rec-mumbai-steel", "laboratory_id": "lab-mumbai", "standard_id": "is-1786", "capabilities": ["Tensile testing", "Chemical analysis", "Bend and rebend"], "source_kind": "DEMO"},
    {"id": "rec-jaipur-hallmark", "laboratory_id": "lab-jaipur", "standard_id": "is-1417", "capabilities": ["Fineness testing", "Assaying demonstration"], "source_kind": "DEMO"},
]

PRODUCT_MANUALS = [{"id": "manual-lighting-demo", "standard_id": "is-10322-5-8", "document_id": "doc-emergency-manual", "source_kind": "DEMO"}]

COMPLIANCE_RULES = [
    {"id": "rule-verified-active-qco", "standard_id": "is-10322-5-8", "name": "Verified active QCO determines mandatory status", "priority": 10, "conditions": {"qco_status": "ACTIVE", "source_verified": True, "effective": True}, "outcome": {"mandatory_status": "MANDATORY"}, "source_kind": "DEMO"},
]

PRODUCTS = [
    {"id": "product-emergency-demo", "name": "Portable rechargeable LED emergency lamp", "category": "Electrical lighting equipment", "source_kind": "DEMO"},
    {"id": "product-kettle-demo", "name": "Electric kettle for household use", "category": "Household electrical appliance", "source_kind": "DEMO"},
    {"id": "product-helmet-demo", "name": "Motorcycle helmet", "category": "Protective rider equipment", "source_kind": "DEMO"},
]

PRODUCT_PROFILES = [
    {"id": "product-profile-emergency-demo", "product_id": "product-emergency-demo", "role": "manufacturer", "input_description": "portable rechargeable LED emergency lamp", "language": "en", "attributes": ["Portable", "Rechargeable battery", "LED light source", "Emergency use"], "missing_attributes": ["rated voltage", "installation type", "battery chemistry"]},
]

COMPLIANCE_PROFILES = [
    {"id": "demo-emergency-lamp", "product_profile_id": "product-profile-emergency-demo", "confidence": 0.91, "mandatory_status": "UNVERIFIED", "qco_id": "qco-lighting-demo", "certification_scheme_id": "scheme-lighting-demo", "tests": ["Marking and construction review", "Insulation resistance", "Electric strength", "Battery endurance", "Emergency-mode photometry"], "required_documents": ["Product specification", "Critical component list", "Circuit diagram", "Test request form", "Manufacturing process flow"], "warnings": ["This profile uses seeded demonstration data.", "Mandatory status and dates have not been verified against a live authoritative BIS source."]},
]

PROFILE_STANDARDS = [{"id": "profile-standard-emergency", "compliance_profile_id": "demo-emergency-lamp", "standard_id": "is-10322-5-8"}]

JOURNEYS = [
    {"id": "journey-emergency-demo", "compliance_profile_id": "demo-emergency-lamp", "steps": [
        {"title": "Classify product", "status": "complete", "explanation": "Lighting equipment → self-contained emergency luminaire"},
        {"title": "Identify candidate standard", "status": "complete", "explanation": "IS 10322 (Part 5/Sec 8):2013"},
        {"title": "Check mandatory status", "status": "attention", "explanation": "Connect current QCO source before relying on this decision", "next_action": "Verify the live regulatory record"},
        {"title": "Review product manual", "status": "pending", "explanation": "Confirm the latest BIS product manual and sampling plan"},
        {"title": "Arrange recognised testing", "status": "pending", "explanation": "Match the exact standard and test scope to a verified lab"},
        {"title": "Prepare application", "status": "pending", "explanation": "Compile technical, manufacturing and test documentation"},
    ]},
]

CITATIONS = [
    {"id": "cite-emergency-scope", "compliance_profile_id": "demo-emergency-lamp", "document_id": "doc-emergency-scope", "chunk_id": "chunk-emergency-scope", "claim": "Emergency luminaire candidate", "source_kind": "DEMO"},
    {"id": "cite-emergency-tests", "compliance_profile_id": "demo-emergency-lamp", "document_id": "doc-emergency-manual", "chunk_id": "chunk-emergency-tests", "claim": "Testing pathway", "source_kind": "DEMO"},
    {"id": "cite-huid-guide", "compliance_profile_id": None, "document_id": "doc-huid-guide", "chunk_id": "chunk-huid-guide", "claim": "HUID verification guidance", "source_kind": "DEMO"},
]
