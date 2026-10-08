from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Schema base com campos comuns"""

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseSchema):
    """Schema base do produto (campos que ProductIn e ProductOut partilham)"""

    name: str = Field(..., description="Nome do produto")
    quantity: int = Field(..., description="Quantidade em estoque")
    price: float = Field(..., description="Preço do produto")
    status: str = Field(..., description="Status do produto (available, unavailable)")


class ProductIn(ProductBase):
    """Schema para os dados de entrada do produto (o que o cliente envia)"""

    pass


class ProductOut(ProductBase):
    """Schema para os dados de saída do produto (o que a API retorna)"""

    uuid: UUID = Field(..., description="ID único do produto")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data da última atualização")


class ProductUpdate(BaseSchema):
    """Schema para atualizar um produto (todos os campos são opcionais)"""

    name: str | None = Field(None, description="Nome do produto")
    quantity: int | None = Field(None, description="Quantidade em estoque")
    price: float | None = Field(None, description="Preço do produto")
    status: str | None = Field(None, description="Status do produto")

    updated_at: datetime | None = Field(
        None, description="Data da última atualização"
    )
