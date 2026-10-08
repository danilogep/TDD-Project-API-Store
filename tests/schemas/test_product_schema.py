from datetime import datetime
from uuid import UUID

from store.schemas.product import ProductOut, ProductUpdate


def test_product_out_schema_should_validate_data_correctly():
    """
    Testa se o schema ProductOut (saída) inclui os campos do banco.
    """
    data = {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": 8500.00,
        "status": "available",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    product = ProductOut(**data)

    assert product.name == "Iphone 14 Pro Max"
    assert isinstance(product.uuid, UUID)
    assert isinstance(product.created_at, datetime)


def test_product_update_schema_should_allow_optional_fields():
    """
    Testa se o schema ProductUpdate aceita apenas um campo (opcional).
    """
    data = {"price": 7500.00}

    product_update = ProductUpdate(**data)

    assert product_update.price == 7500.00
    # Garante que os outros campos são None, e não obrigatórios
    assert product_update.name is None
    assert product_update.quantity is None
    assert product_update.status is None
