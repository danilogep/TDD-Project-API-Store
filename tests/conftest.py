"""Infraestrutura dos testes.

A suíte fala com um **MongoDB de verdade** — não com um dobro em memória. A razão
é direta: boa parte do que esta API faz é tradução entre Pydantic e BSON (UUID
nativo, `datetime` com fuso, operadores `$gt`/`$lt`/`$set`). Um mock de dicionário
concorda com qualquer coisa que o repositório faça e passaria verde justamente
nos pontos em que o banco reprovaria.

Para que isso não custe nada a quem clonou o projeto, o banco sobe sozinho:

* **`poetry run pytest`** — sem configurar nada. O [testcontainers] levanta um
  `mongo:7` descartável, roda a suíte e derruba o container no fim. Basta ter
  Docker no ambiente.
* **`MONGODB_URL_TEST=mongodb://localhost:27017 poetry run pytest`** — usa um
  servidor que já esteja no ar. É assim que o CI roda, contra o serviço `mongo`
  do GitHub Actions, e é o atalho para quem já mantém um Mongo local.

`MONGODB_URL` (a do `.env`, que aponta para o banco da aplicação) **nunca** é
usada aqui: teste que derruba coleção não escolhe sozinho o servidor onde vai
fazer isso.

[testcontainers]: https://testcontainers.com/
"""

import os
from datetime import UTC

import motor.motor_asyncio
import pytest
from httpx import ASGITransport, AsyncClient

from store.core.config import settings
from store.core.db import get_db
from store.main import app

IMAGEM_MONGO = "mongo:7.0"


@pytest.fixture(scope="session")
def mongo_url():
    """URL do MongoDB de teste, de um servidor existente ou de um container efêmero."""
    url = os.getenv("MONGODB_URL_TEST")
    if url:
        yield url
        return

    try:
        from testcontainers.mongodb import MongoDbContainer
    except ImportError:  # pragma: no cover - só acontece em instalação incompleta
        pytest.fail(
            "Instale as dependências de desenvolvimento (`poetry install`) ou "
            "aponte MONGODB_URL_TEST para um MongoDB acessível."
        )

    container = MongoDbContainer(IMAGEM_MONGO)
    try:
        container.start()
    except Exception as erro:  # pragma: no cover - ambiente sem Docker
        pytest.fail(
            f"Não foi possível subir o MongoDB de teste ({IMAGEM_MONGO}): {erro}\n"
            "Suba o Docker ou defina MONGODB_URL_TEST apontando para um servidor."
        )

    url = container.get_connection_url()
    yield url
    container.stop()


@pytest.fixture(scope="function")
async def db_client(mongo_url):
    """Ligação ao banco de teste, limpa a cada teste."""
    cliente = motor.motor_asyncio.AsyncIOMotorClient(
        mongo_url,
        uuidRepresentation="standard",
        tz_aware=True,
        tzinfo=UTC,
    )
    db = cliente[settings.MONGODB_DB_NAME_TEST]

    # Limpa antes e depois: um teste interrompido no meio não contamina o próximo.
    await db.drop_collection("products")

    yield db

    await db.drop_collection("products")
    cliente.close()


@pytest.fixture(scope="function")
async def client(db_client):
    """Cliente HTTP com a dependência de banco da aplicação já substituída."""
    app.dependency_overrides[get_db] = lambda: db_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def produto_payload():
    """Payload válido de produto. Cada teste sobrescreve o que precisar."""

    def _payload(**overrides):
        base = {
            "name": "Iphone 14 Pro Max",
            "quantity": 10,
            "price": 8500.00,
            "status": "available",
        }
        base.update(overrides)
        return base

    return _payload
