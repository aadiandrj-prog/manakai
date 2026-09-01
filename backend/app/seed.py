import argparse

from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal, engine
from .db_models import (
    Base,
    CertificationScheme,
    Citation,
    ComplianceJourney,
    ComplianceProfile,
    ComplianceProfileStandard,
    ComplianceRule,
    Document,
    DocumentChunk,
    Laboratory,
    LaboratoryRecognition,
    Product,
    ProductManual,
    ProductProfile,
    QCO,
    Standard,
    StandardQCO,
    StandardRelationship,
    Test,
)
from . import seed_data


SEED_GROUPS = [
    (Standard, seed_data.STANDARDS),
    (StandardRelationship, seed_data.STANDARD_RELATIONSHIPS),
    (Document, seed_data.DOCUMENTS),
    (DocumentChunk, seed_data.DOCUMENT_CHUNKS),
    (QCO, seed_data.QCOS),
    (StandardQCO, seed_data.STANDARD_QCOS),
    (CertificationScheme, seed_data.CERTIFICATION_SCHEMES),
    (Test, seed_data.TESTS),
    (Laboratory, seed_data.LABORATORIES),
    (LaboratoryRecognition, seed_data.LABORATORY_RECOGNITIONS),
    (ProductManual, seed_data.PRODUCT_MANUALS),
    (ComplianceRule, seed_data.COMPLIANCE_RULES),
    (Product, seed_data.PRODUCTS),
    (ProductProfile, seed_data.PRODUCT_PROFILES),
    (ComplianceProfile, seed_data.COMPLIANCE_PROFILES),
    (ComplianceProfileStandard, seed_data.PROFILE_STANDARDS),
    (ComplianceJourney, seed_data.JOURNEYS),
    (Citation, seed_data.CITATIONS),
]


def seed_database(session: Session) -> None:
    for model, rows in SEED_GROUPS:
        with session.no_autoflush:
            for row in rows:
                session.merge(model(**row))
        session.commit()


def reset_demo_database() -> None:
    if not settings.demo_mode:
        raise RuntimeError("Database reset is available only when DEMO_MODE=true")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        seed_database(session)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed ManakAI demo data")
    parser.add_argument("--reset", action="store_true", help="Drop/recreate tables before seeding (DEMO_MODE only)")
    args = parser.parse_args()
    if args.reset:
        reset_demo_database()
        return
    with SessionLocal() as session:
        seed_database(session)


if __name__ == "__main__":
    main()
