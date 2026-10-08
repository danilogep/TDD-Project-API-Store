from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from store.models.product import ProductModel
from store.repositories.product import ProductRepository
from store.schemas.product import ProductIn, ProductOut, ProductUpdate
from store.usecases.product import ProductUsecase


@pytest.mark.asyncio
async def test_usecase_create_should_return_product_out():
    # 1. Prepara os dados de entrada
    product_in = ProductIn(
        name="Iphone 14 Pro Max", quantity=10, price=8500.00, status="available"
    )

    # 2. Cria um 'mock' do repositório
    mock_repo = MagicMock(spec=ProductRepository)
    mock_repo.create = AsyncMock(return_value=True)

    # 3. Instancia o Usecase
    usecase = ProductUsecase(repository=mock_repo)

    # 4. Chama o método 'create'
    product_out = await usecase.create(body=product_in)

    # 5. Verifica se o resultado é um ProductOut
    assert isinstance(product_out, ProductOut)
    assert product_out.name == "Iphone 14 Pro Max"
    assert str(product_out.uuid)


@pytest.mark.asyncio
async def test_usecase_list_should_return_list_of_product_out():
    # 1. Crie dados "falsos" do modelo
    fake_products = [
        ProductModel(name="Iphone 14", quantity=10, price=8500, status="available"),
        ProductModel(name="Iphone 15", quantity=5, price=10500, status="available"),
    ]

    # 2. Crie um 'mock' do repositório
    mock_repo = MagicMock(spec=ProductRepository)
    mock_repo.list = AsyncMock(return_value=fake_products)

    # 3. Instancia o Usecase
    usecase = ProductUsecase(repository=mock_repo)

    # 4. Chama o método 'list'
    products_out = await usecase.list()

    # 5. Verifica se os dados foram convertidos
    assert isinstance(products_out, list)
    assert len(products_out) == 2
    assert isinstance(products_out[0], ProductOut)
    assert products_out[0].name == "Iphone 14"


@pytest.mark.asyncio
async def test_usecase_get_should_return_product_out():
    # 1. Crie dados "falsos" do modelo
    fake_uuid = uuid4()
    fake_product = ProductModel(
        uuid=fake_uuid, name="Iphone 14", quantity=10, price=8500, status="available"
    )

    # 2. Crie um 'mock' do repositório
    mock_repo = MagicMock(spec=ProductRepository)
    mock_repo.get = AsyncMock(return_value=fake_product)

    # 3. Instancia o Usecase
    usecase = ProductUsecase(repository=mock_repo)

    # 4. Chama o método 'get'
    product_out = await usecase.get(uuid=fake_uuid)

    # 5. Verifica se os dados foram convertidos
    assert isinstance(product_out, ProductOut)
    assert product_out.name == "Iphone 14"
    assert product_out.uuid == fake_uuid


@pytest.mark.asyncio
async def test_usecase_update_should_return_product_out():
    # 1. Defina o UUID e os dados de atualização
    fake_uuid = uuid4()
    product_update = ProductUpdate(price=7500.00)

    # 2. Crie um "mock" do produto como ele será retornado pelo repositório
    fake_product_updated = ProductModel(
        uuid=fake_uuid,
        name="Iphone 14",
        quantity=10,
        price=7500.00,  # Preço atualizado
        status="available",
    )

    # 3. Crie um 'mock' do repositório
    mock_repo = MagicMock(spec=ProductRepository)
    mock_repo.update = AsyncMock(return_value=fake_product_updated)

    # 4. Instancia o Usecase
    usecase = ProductUsecase(repository=mock_repo)

    # 5. Chama o método 'update'
    product_out = await usecase.update(uuid=fake_uuid, body=product_update)

    # 6. Verifica se o resultado é o ProductOut correto
    assert isinstance(product_out, ProductOut)
    assert product_out.price == 7500.00
    assert product_out.uuid == fake_uuid


@pytest.mark.asyncio
async def test_usecase_delete_should_return_true(db_client):
    # 1. Defina o UUID
    fake_uuid = uuid4()

    # 2. Crie um 'mock' do repositório
    mock_repo = MagicMock(spec=ProductRepository)
    # Simule que o método 'delete' retorna True
    mock_repo.delete = AsyncMock(return_value=True)

    # 3. Instancia o Usecase
    usecase = ProductUsecase(repository=mock_repo)

    # 4. Chama o método 'delete' (que ainda não existe)
    deleted = await usecase.delete(uuid=fake_uuid)

    # 5. Verifica se o resultado é True
    assert deleted is True
