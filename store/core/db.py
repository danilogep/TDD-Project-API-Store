import motor.motor_asyncio
from store.core.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import timezone


class MongoClient:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGODB_URL,
            uuidRepresentation="standard",
            tz_aware=True,
            tzinfo=timezone.utc,
        )

    def get_database(self, db_name: str) -> AsyncIOMotorDatabase:
        return self.client[db_name]


mongo_client = MongoClient()


def get_db() -> AsyncIOMotorDatabase:
    return mongo_client.get_database(settings.MONGODB_DB_NAME)
