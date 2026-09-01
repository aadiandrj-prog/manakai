from .schemas import Citation, Laboratory, RegulatoryStatus, SourceKind, Standard


STANDARDS = [
    Standard(id="is-10322-5-8", number="IS 10322 (Part 5/Sec 8)", title="Luminaires — Particular requirements: emergency lighting", version="2013", status=RegulatoryStatus.ACTIVE, category="Electrical", scope="Demo scope record for emergency-lighting luminaires."),
    Standard(id="is-302-2-15", number="IS 302 (Part 2/Sec 15)", title="Safety of household electrical appliances — Appliances for heating liquids", version="2009", status=RegulatoryStatus.AMENDED, category="Electrical", scope="Demo scope record for household appliances used to heat liquids."),
    Standard(id="is-4151", number="IS 4151", title="Protective helmets for scooter and motorcycle riders", version="2015", status=RegulatoryStatus.ACTIVE, category="Consumer safety", scope="Demo scope record for protective rider helmets."),
    Standard(id="is-1786", number="IS 1786", title="High strength deformed steel bars and wires for concrete reinforcement", version="2008", status=RegulatoryStatus.AMENDED, category="Construction", scope="Demo scope record for reinforcement steel."),
    Standard(id="is-1417", number="IS 1417", title="Gold and gold alloys, jewellery/artefacts — fineness and marking", version="2016", status=RegulatoryStatus.ACTIVE, category="Hallmarking", scope="Demo scope record supporting hallmarking guidance."),
]

LABORATORIES = [
    Laboratory(id="lab-delhi", name="Northstar Electrical Test Lab", city="New Delhi", state="Delhi", standards=["IS 10322 (Part 5/Sec 8)", "IS 302 (Part 2/Sec 15)"], capabilities=["Electrical safety", "Insulation resistance", "Endurance"]),
    Laboratory(id="lab-noida", name="Apex Product Assurance Centre", city="Noida", state="Uttar Pradesh", standards=["IS 4151", "IS 10322 (Part 5/Sec 8)"], capabilities=["Impact testing", "Photometry", "Thermal testing"]),
    Laboratory(id="lab-mumbai", name="Western Materials Validation Lab", city="Mumbai", state="Maharashtra", standards=["IS 1786"], capabilities=["Tensile testing", "Chemical analysis", "Bend and rebend"]),
]

CITATIONS = [
    Citation(id="cite-emergency-scope", document_title="Emergency lighting standard metadata", document_type="Indian Standard metadata", standard_number="IS 10322 (Part 5/Sec 8)", version="2013", source_kind=SourceKind.DEMO),
    Citation(id="cite-emergency-tests", document_title="Emergency luminaire product manual mapping", document_type="Demo product manual", standard_number="IS 10322 (Part 5/Sec 8)", source_kind=SourceKind.DEMO),
    Citation(id="cite-huid-guide", document_title="Hallmarking consumer guidance fixture", document_type="Consumer guidance", standard_number="IS 1417", source_kind=SourceKind.DEMO),
]
