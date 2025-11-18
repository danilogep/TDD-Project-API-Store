# Em store/core/db.py

import motor.motor_asyncio
from store.core.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import timezone  # 1. Importe timezone


class MongoClient:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGODB_URL,
            uuidRepresentation="standard",
            tz_aware=True,  # 2. Adicione esta linha
            tzinfo=timezone.utc,  # 3. Adicione esta linha
        )

    def get_database(self, db_name: str) -> AsyncIOMotorDatabase:
        return self.client[db_name]


# Criamos a instância, mas não a base de dados
mongo_client = MongoClient()


# Esta é a nossa nova dependência: ela obtém a BD de produção
def get_db() -> AsyncIOMotorDatabase:
    return mongo_client.get_database(settings.MONGODB_DB_NAME)
