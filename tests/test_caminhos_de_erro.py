"""Os caminhos que ninguém exercita à mão.

O caminho feliz aparece sozinho durante o desenvolvimento: a gente roda, vê
funcionar e segue. O que some do radar é o 404 de um UUID que não existe e o
erro do banco em uma hora ruim. São exatamente os que este arquivo trava, e são
os que levaram a cobertura de 95% para 100%.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from pymongo.errors import PyMongoError

from store.core.exceptions import DatabaseException
from store.repositories.product import ProductRepository
from store.schemas.product import ProductIn, ProductUpdate
from store.usecases.product import ProductUsecase

UUID_INEXISTENTE = "00000000-0000-4000-8000-000000000000"


# --- Controller -------------------------------------------------------------


async def test_get_de_uuid_inexistente_devolve_404(client):
    response = await client.get(f"/products/{UUID_INEXISTENTE}")

    assert response.status_code == 404
    assert UUID_INEXISTENTE in response.json()["detail"]


async def test_put_de_uuid_inexistente_devolve_404(client):
    response = await client.put(f"/products/{UUID_INEXISTENTE}", json={"price": 10.0})

    assert response.status_code == 404
    assert UUID_INEXISTENTE in response.json()["detail"]


async def test_delete_de_uuid_inexistente_devolve_404(client):
    response = await client.delete(f"/products/{UUID_INEXISTENTE}")

    assert response.status_code == 404


async def test_uuid_malformado_devolve_422(client):
    """Validação de rota: `nao-e-um-uuid` nem chega ao banco."""
    response = await client.get("/products/nao-e-um-uuid")

    assert response.status_code == 422


# --- Repositório ------------------------------------------------------------


async def test_update_sem_documento_correspondente_devolve_none(db_client):
    repo = ProductRepository(db_client)

    resultado = await repo.update(uuid4(), ProductUpdate(price=10.0))

    assert resultado is None


async def test_delete_sem_documento_correspondente_devolve_false(db_client):
    repo = ProductRepository(db_client)

    assert await repo.delete(uuid4()) is False


async def test_get_sem_documento_correspondente_devolve_none(db_client):
    repo = ProductRepository(db_client)

    assert await repo.get(uuid4()) is None


# --- Usecase ----------------------------------------------------------------


async def test_falha_do_banco_vira_database_exception():
    """O usecase traduz o erro do driver para a exceção da aplicação.

    É o que permite ao controller devolver 500 com uma mensagem própria sem
    conhecer o PyMongo — a camada de cima não deve saber qual banco existe lá
    embaixo.
    """
    mock_repo = MagicMock(spec=ProductRepository)
    mock_repo.create = AsyncMock(side_effect=PyMongoError("conexão perdida"))

    usecase = ProductUsecase(repository=mock_repo)

    with pytest.raises(DatabaseException) as erro:
        await usecase.create(
            body=ProductIn(name="Iphone", quantity=1, price=10.0, status="available")
        )

    assert "conexão perdida" in str(erro.value)


async def test_update_de_produto_inexistente_devolve_none():
    mock_repo = MagicMock(spec=ProductRepository)
    mock_repo.update = AsyncMock(return_value=None)

    usecase = ProductUsecase(repository=mock_repo)

    assert await usecase.update(uuid=uuid4(), body=ProductUpdate(price=10.0)) is None


async def test_update_preenche_updated_at_quando_nao_vem_no_corpo():
    """Regra do desafio: o `updated_at` é carimbado quando o cliente não o manda."""
    mock_repo = MagicMock(spec=ProductRepository)
    mock_repo.update = AsyncMock(return_value=None)

    usecase = ProductUsecase(repository=mock_repo)
    body = ProductUpdate(price=10.0)
    assert body.updated_at is None

    await usecase.update(uuid=uuid4(), body=body)

    assert body.updated_at is not None


# --- Fábrica de conexão -----------------------------------------------------


def test_get_db_resolve_o_banco_da_aplicacao():
    """`get_db` é a dependência que os testes substituem — e por isso nunca roda.

    Motor só abre socket na primeira operação, então instanciar o handle aqui
    não encosta em servidor nenhum: o que se verifica é o nome resolvido.
    """
    from store.core.config import settings
    from store.core.db import get_db, mongo_client

    assert get_db().name == settings.MONGODB_DB_NAME
    # Sem argumento, cai no banco da aplicação em vez de estourar TypeError.
    assert mongo_client.get_database().name == settings.MONGODB_DB_NAME
