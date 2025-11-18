# Em store/schemas/product.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime  # 1. Certifique-se que datetime está importado


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

    name: Optional[str] = Field(None, description="Nome do produto")
    quantity: Optional[int] = Field(None, description="Quantidade em estoque")
    price: Optional[float] = Field(None, description="Preço do produto")
    status: Optional[str] = Field(None, description="Status do produto")

    # 2. ADICIONE ESTA LINHA (desafio final)
    updated_at: Optional[datetime] = Field(
        None, description="Data da última atualização"
    )
