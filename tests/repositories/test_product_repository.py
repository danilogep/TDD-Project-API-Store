
import pytest

from store.models.product import ProductModel
from store.repositories.product import ProductRepository
from store.schemas.product import ProductUpdate


@pytest.mark.asyncio
async def test_repository_create_should_insert_product_in_db(db_client):
    # 1. Prepara os dados do modelo
    product_model = ProductModel(
        name="Iphone 14 Pro Max", quantity=10, price=8500.00, status="available"
    )

    # 2. Instancia o repositório
    repo = ProductRepository(db_client)

    # 3. Chama o método 'create'
    await repo.create(product_model)

    # 4. Verifica se o dado foi realmente inserido no banco
    inserted = await db_client["products"].find_one({"uuid": product_model.uuid})

    assert inserted is not None
    assert inserted["name"] == "Iphone 14 Pro Max"
    assert inserted["price"] == 8500.00


@pytest.mark.asyncio
async def test_repository_list_should_return_products(db_client):
    # 1. Insere dois produtos no banco de teste
    await db_client["products"].insert_many(
        [
            ProductModel(
                name="Iphone 14", quantity=10, price=8500, status="available"
            ).model_dump(),
            ProductModel(
                name="Iphone 15", quantity=5, price=10500, status="available"
            ).model_dump(),
        ]
    )

    # 2. Instancia o repositório
    repo = ProductRepository(db_client)

    # 3. Chama o método 'list'
    products = await repo.list()

    # 4. Verifica se os dados foram retornados
    assert isinstance(products, list)
    assert len(products) == 2
    assert products[0].name == "Iphone 14"


@pytest.mark.asyncio
async def test_repository_get_should_return_product(db_client):
    # 1. Insere um produto
    product_model = ProductModel(
        name="Iphone 14", quantity=10, price=8500, status="available"
    )
    await db_client["products"].insert_one(product_model.model_dump())

    # 2. Instancia o repositório
    repo = ProductRepository(db_client)

    # 3. Chama o método 'get'
    product = await repo.get(product_model.uuid)

    # 4. Verifica se os dados foram retornados
    assert product is not None
    assert isinstance(product, ProductModel)
    assert product.name == "Iphone 14"
    assert product.uuid == product_model.uuid


@pytest.mark.asyncio
async def test_repository_update_should_return_product(db_client):
    # 1. Insere um produto
    product_model = ProductModel(
        name="Iphone 14", quantity=10, price=8500, status="available"
    )
    await db_client["products"].insert_one(product_model.model_dump())

    # 2. Dados para atualizar
    product_update = ProductUpdate(price=7500.00, status="unavailable")

    # 3. Instancia o repositório
    repo = ProductRepository(db_client)

    # 4. Chama o método 'update'
    updated_product = await repo.update(product_model.uuid, product_update)

    # 5. Verifica se o produto foi atualizado
    assert updated_product is not None
    assert isinstance(updated_product, ProductModel)
    assert updated_product.price == 7500.00
    assert updated_product.status == "unavailable"


@pytest.mark.asyncio
async def test_repository_delete_should_remove_product(db_client):
    # 1. Insere um produto
    product_model = ProductModel(
        name="Iphone 14", quantity=10, price=8500, status="available"
    )
    await db_client["products"].insert_one(product_model.model_dump())

    # 2. Instancia o repositório
    repo = ProductRepository(db_client)

    # 3. Chama o método 'delete' (que ainda não existe)
    deleted = await repo.delete(product_model.uuid)

    # 4. Verifica se o método retornou True
    assert deleted is True

    # 5. Verifica se o produto foi mesmo apagado do banco
    product = await repo.get(product_model.uuid)
    assert product is None
