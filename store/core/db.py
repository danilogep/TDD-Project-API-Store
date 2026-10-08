from datetime import UTC

import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase

from store.core.config import settings


class MongoClient:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGODB_URL,
            uuidRepresentation="standard",
            tz_aware=True,
            tzinfo=UTC,
        )

    def get_database(self, db_name: str | None = None) -> AsyncIOMotorDatabase:
        # Sem nome explicito usa o banco da aplicacao. Antes o parametro era
        # obrigatorio, e o caminho padrao do ProductRepository (sem injecao de
        # dependencia) estourava TypeError.
        return self.client[db_name or settings.MONGODB_DB_NAME]


mongo_client = MongoClient()


def get_db() -> AsyncIOMotorDatabase:
    return mongo_client.get_database(settings.MONGODB_DB_NAME)
