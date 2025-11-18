from pydantic import UUID4, Field
from uuid import uuid4
from datetime import datetime, timezone
from store.schemas.product import ProductBase


class ProductModel(ProductBase):
    """
    Modelo do produto como é armazenado na base de dados.
    """

    uuid: UUID4 = Field(default_factory=uuid4)

    # 2. Use datetime.now(timezone.utc) para consistência
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
