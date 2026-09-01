from uuid import uuid4

from sqlalchemy.orm import Session

from ..db_models import Product, ProductProfile


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_profile(
        self,
        *,
        name: str,
        category: str,
        role: str,
        description: str,
        language: str,
        attributes: list[str],
        missing_attributes: list[str],
    ) -> ProductProfile:
        product = Product(id=f"product-{uuid4().hex}", name=name, category=category, source_kind="demo")
        profile = ProductProfile(
            id=f"product-profile-{uuid4().hex}",
            product=product,
            role=role,
            input_description=description,
            language=language,
            attributes=attributes,
            missing_attributes=missing_attributes,
        )
        self.session.add(profile)
        self.session.flush()
        return profile
