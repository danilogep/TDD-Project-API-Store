# Em tests/conftest.py

import pytest
import motor.motor_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import timezone  # 1. Importe timezone

from store.core.config import settings
from store.main import app
from store.core.db import get_db  # Importe a dependência que queremos substituir


# Fixture 1: Para testes de API (Controller)
@pytest.fixture(scope="function")
async def client():
    """
    Fornece um cliente HTTP que já está configurado
    para usar a base de dados de teste.
    """

    # Crie uma ligação à BD de TESTE *apenas para este cliente*
    db_client_motor = motor.motor_asyncio.AsyncIOMotorClient(
        settings.MONGODB_URL,
        uuidRepresentation="standard",
        tz_aware=True,  # 2. Adicione esta linha
        tzinfo=timezone.utc,  # 3. Adicione esta linha
    )
    db = db_client_motor[settings.MONGODB_DB_NAME_TEST]

    # Função de substituição
    def override_get_db():
        return db

    # Aplique a substituição
    app.dependency_overrides[get_db] = override_get_db

    # Crie o cliente HTTP
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac  # O TESTE EXECUTA AQUI

    # Limpe a base de dados de teste
    await db.drop_collection("products")
    db_client_motor.close()

    # Limpe a substituição
    app.dependency_overrides.clear()


# Fixture 2: Para testes diretos de Repositório
@pytest.fixture(scope="function")
async def db_client():
    """
    Fornece uma ligação direta à base de dados de teste
    para os testes de repositório.
    """

    # Crie uma ligação à BD de TESTE *apenas para este teste*
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.MONGODB_URL,
        uuidRepresentation="standard",
        tz_aware=True,  # 4. Adicione esta linha
        tzinfo=timezone.utc,  # 5. Adicione esta linha
    )
    db = client[settings.MONGODB_DB_NAME_TEST]

    yield db  # O TESTE EXECUTA AQUI

    # Limpe a base de dados
    await db.drop_collection("products")
    client.close()
