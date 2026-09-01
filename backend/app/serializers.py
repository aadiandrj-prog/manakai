from collections import defaultdict

from . import db_models as models
from . import schemas


def standard_to_schema(standard: models.Standard) -> schemas.Standard:
    return schemas.Standard.model_validate(standard)


def relationship_to_schema(relationship: models.StandardRelationship) -> schemas.StandardRelationship:
    return schemas.StandardRelationship(
        id=relationship.id,
        relationship_type=relationship.relationship_type,
        source_standard_id=relationship.source_standard_id,
        target_standard=standard_to_schema(relationship.target),
    )


def recognitions_to_laboratories(recognitions: list[models.LaboratoryRecognition]) -> list[schemas.Laboratory]:
    grouped: dict[str, dict] = defaultdict(lambda: {"standards": [], "capabilities": [], "test_clauses": []})
    for recognition in recognitions:
        item = grouped[recognition.laboratory_id]
        item["laboratory"] = recognition.laboratory
        item["standards"].append(recognition.standard.number)
        item["capabilities"].extend(recognition.capabilities or [])
        item["test_clauses"].extend(recognition.test_clauses or [])
        item["recognition"] = recognition
    result = []
    for item in grouped.values():
        laboratory = item["laboratory"]
        recognition = item["recognition"]
        result.append(
            schemas.Laboratory(
                id=laboratory.id,
                name=laboratory.name,
                city=laboratory.city,
                state=laboratory.state,
                address=laboratory.address,
                standards=sorted(set(item["standards"])),
                capabilities=sorted(set(item["capabilities"])),
                source_kind=laboratory.source_kind,
                scope_identifier=recognition.scope_identifier,
                scope=recognition.scope,
                test_clauses=sorted(set(item["test_clauses"])),
                valid_from=recognition.valid_from,
                valid_until=recognition.valid_until,
                recognition_status=recognition.status,
                source_url=recognition.source_url,
                retrieved_at=recognition.retrieved_at,
                warning=None if recognition.valid_until else "Recognition validity could not be confirmed from the stored source.",
            )
        )
    return sorted(result, key=lambda lab: lab.name)


def citation_to_schema(citation: models.Citation) -> schemas.Citation:
    document = citation.document
    chunk = citation.chunk
    return schemas.Citation(
        id=citation.id,
        document_title=document.title,
        document_type=document.document_type,
        standard_number=document.standard.number if document.standard else None,
        version=document.version,
        page=chunk.page if chunk else None,
        clause=chunk.clause if chunk else None,
        source_url=document.source_url,
        publication_date=document.publication_date,
        effective_date=document.effective_date,
        retrieved_at=document.retrieved_at,
        source_kind=citation.source_kind,
        source_authority=document.source_authority,
        document_identifier=document.document_identifier,
        status=document.status,
        verification_status=document.verification_status,
        claim=citation.claim,
        validation_status=citation.validation_status,
    )


def document_to_schema(document: models.Document) -> schemas.Document:
    return schemas.Document(
        id=document.id,
        title=document.title,
        document_type=document.document_type,
        standard_id=document.standard_id,
        standard_number=document.standard.number if document.standard else None,
        version=document.version,
        source_url=document.source_url,
        publication_date=document.publication_date,
        effective_date=document.effective_date,
        retrieved_at=document.retrieved_at,
        source_kind=document.source_kind,
    )
