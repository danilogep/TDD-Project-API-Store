import asyncio
from datetime import datetime

import pytest
from httpx import AsyncClient

from store.core.exceptions import DatabaseException
from store.usecases.product import ProductUsecase


@pytest.mark.asyncio
async def test_create_product_should_return_201(client: AsyncClient):
    # ... (teste 'create' normal)
    payload = {
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": 8500.00,
        "status": "available",
    }
    response = await client.post("/products/", json=payload)
    assert response.status_code == 201
    response_data = response.json()
    assert "uuid" in response_data
    assert response_data["name"] == "Iphone 14 Pro Max"


@pytest.mark.asyncio
async def test_list_products_should_return_200(client: AsyncClient):
    # ... (teste 'list' normal)
    payload = {
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": 8500.00,
        "status": "available",
    }
    response_post = await client.post("/products/", json=payload)
    assert response_post.status_code == 201

    response_get = await client.get("/products/")

    assert response_get.status_code == 200
    response_data = response_get.json()
    assert isinstance(response_data, list)
    assert len(response_data) > 0
    assert response_data[0]["name"] == "Iphone 14 Pro Max"


@pytest.mark.asyncio
async def test_get_product_should_return_200(client: AsyncClient):
    # ... (teste 'get' normal)
    payload = {
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": 8500.00,
        "status": "available",
    }
    response_post = await client.post("/products/", json=payload)
    assert response_post.status_code == 201

    product_uuid = response_post.json()["uuid"]

    response_get = await client.get(f"/products/{product_uuid}")

    assert response_get.status_code == 200
    response_data = response_get.json()
    assert response_data["uuid"] == product_uuid
    assert response_data["name"] == "Iphone 14 Pro Max"


@pytest.mark.asyncio
async def test_update_product_should_return_200(client: AsyncClient):
    # ... (teste 'update' normal)
    payload = {
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": 8500.00,
        "status": "available",
    }
    response_post = await client.post("/products/", json=payload)
    assert response_post.status_code == 201
    product_uuid = response_post.json()["uuid"]

    update_payload = {"price": 7500.00}

    response_put = await client.put(f"/products/{product_uuid}", json=update_payload)

    assert response_put.status_code == 200
    response_data = response_put.json()
    assert response_data["price"] == 7500.00
    assert response_data["name"] == "Iphone 14 Pro Max"


@pytest.mark.asyncio
async def test_delete_product_should_return_204(client: AsyncClient):
    # ... (teste 'delete' normal)
    payload = {
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": 8500.00,
        "status": "available",
    }
    response_post = await client.post("/products/", json=payload)
    assert response_post.status_code == 201
    product_uuid = response_post.json()["uuid"]

    response_delete = await client.delete(f"/products/{product_uuid}")

    assert response_delete.status_code == 204

    response_get = await client.get(f"/products/{product_uuid}")
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_create_product_should_return_500_on_db_error(
    client: AsyncClient, monkeypatch
):
    # ... (teste de erro 500)
    async def mock_create_raises(*args, **kwargs):
        raise DatabaseException("Erro simulado do banco de dados")

    monkeypatch.setattr(ProductUsecase, "create", mock_create_raises)

    payload = {
        "name": "Produto com Erro",
        "quantity": 10,
        "price": 8500.00,
        "status": "available",
    }

    response = await client.post("/products/", json=payload)

    assert response.status_code == 500
    assert response.json() == {"detail": "Ocorreu um erro ao inserir o produto."}


@pytest.mark.asyncio
async def test_update_product_should_auto_update_updated_at(client: AsyncClient):
    # ... (teste 'auto_update' do desafio)
    payload = {
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": 8500.00,
        "status": "available",
    }
    response_post = await client.post("/products/", json=payload)
    assert response_post.status_code == 201

    product_uuid = response_post.json()["uuid"]
    original_updated_at = datetime.fromisoformat(response_post.json()["updated_at"])

    await asyncio.sleep(0.001)

    update_payload = {"price": 7500.00}

    response_put = await client.put(f"/products/{product_uuid}", json=update_payload)
    assert response_put.status_code == 200

    new_updated_at = datetime.fromisoformat(response_put.json()["updated_at"])
    assert new_updated_at > original_updated_at


@pytest.mark.asyncio
async def test_update_product_should_allow_manual_updated_at(client: AsyncClient):
    # ... (teste 'manual_update' do desafio)
    payload = {
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": 8500.00,
        "status": "available",
    }
    response_post = await client.post("/products/", json=payload)
    assert response_post.status_code == 201
    product_uuid = response_post.json()["uuid"]

    manual_date_str = "2000-01-01T00:00:00+00:00"
    manual_date = datetime.fromisoformat(manual_date_str)

    update_payload = {"price": 7500.00, "updated_at": manual_date_str}

    response_put = await client.put(f"/products/{product_uuid}", json=update_payload)
    assert response_put.status_code == 200

    new_updated_at = datetime.fromisoformat(response_put.json()["updated_at"])
    assert new_updated_at == manual_date


@pytest.mark.asyncio
async def test_list_products_should_filter_by_price(client: AsyncClient):
    # 1. Cria vários produtos com preços diferentes
    await client.post(
        "/products/",
        json={
            "name": "Produto 1",
            "quantity": 10,
            "price": 4000,
            "status": "available",
        },
    )
    await client.post(
        "/products/",
        json={
            "name": "Produto 2",
            "quantity": 10,
            "price": 6000,
            "status": "available",
        },
    )
    await client.post(
        "/products/",
        json={
            "name": "Produto 3",
            "quantity": 10,
            "price": 7500,
            "status": "available",
        },
    )
    await client.post(
        "/products/",
        json={
            "name": "Produto 4",
            "quantity": 10,
            "price": 9000,
            "status": "available",
        },
    )

    # 2. Faz a chamada GET com os filtros (isto vai falhar)
    response_get = await client.get("/products/?price_min=5000&price_max=8000")

    # 3. Verifica a resposta
    assert response_get.status_code == 200

    response_data = response_get.json()
    assert isinstance(response_data, list)

    # 4. Verifica se *apenas* os produtos no intervalo foram retornados
    assert len(response_data) == 2
    prices = sorted([item["price"] for item in response_data])
    assert prices == [6000, 7500]
