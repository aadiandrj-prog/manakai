from ..fixtures import CITATIONS, LABORATORIES, STANDARDS
from ..schemas import ComplianceProfile, JourneyStep, ProductAnalyseRequest, ProductProfile


def _match_standard(description: str):
    text = description.casefold()
    if "kettle" in text or "boil" in text:
        return STANDARDS[1], "Household liquid-heating appliance", ["Electric heating", "Household use"]
    if "helmet" in text:
        return STANDARDS[2], "Protective rider equipment", ["Head protection", "Two-wheeler use"]
    if "steel" in text or "rebar" in text:
        return STANDARDS[3], "Construction reinforcement material", ["Deformed bar", "Concrete reinforcement"]
    return STANDARDS[0], "Electrical lighting equipment", ["Portable", "Rechargeable battery", "LED light source", "Emergency use"]


def analyse_product(request: ProductAnalyseRequest) -> ComplianceProfile:
    standard, category, attributes = _match_standard(request.description)
    labs = [lab for lab in LABORATORIES if standard.number in lab.standards]
    product = ProductProfile(interpreted_product=request.description.strip(), role=request.role, category=category, attributes=attributes, missing_attributes=["rated voltage", "installation type", "battery chemistry"])
    return ComplianceProfile(
        id="demo-emergency-lamp",
        product=product,
        applicable_standards=[standard],
        mandatory_status="UNVERIFIED",
        qco=None,
        certification_scheme=None,
        tests=["Construction and marking review", "Insulation resistance", "Electric strength", "Endurance", "Product-specific performance testing"],
        required_documents=["Product specification", "Critical component list", "Circuit diagram", "Manufacturing process flow"],
        laboratories=labs,
        next_steps=[
            JourneyStep(title="Classify product", status="complete", explanation=category),
            JourneyStep(title="Identify candidate standard", status="complete", explanation=standard.number),
            JourneyStep(title="Verify QCO and scheme", status="attention", explanation="No live authoritative source is connected", next_action="Check current BIS/QCO source"),
            JourneyStep(title="Arrange recognised testing", status="pending", explanation="Confirm exact recognition scope before engagement"),
        ],
        evidence=[item for item in CITATIONS if item.standard_number == standard.number],
        confidence=0.91 if standard == STANDARDS[0] else 0.82,
        warnings=["DEMO_MODE is active.", "Mandatory status and effective dates are not verified."],
    )
