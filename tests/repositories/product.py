from motor.motor_asyncio import AsyncIOMotorDatabase
from store.models.product import ProductModel
from store.core.db import mongo_client


class ProductRepository:
    def __init__(self, db_client: AsyncIOMotorDatabase = None):
        # Permite injetar um DB (para testes) ou usa o principal
        self.db = db_client or mongo_client.get_database()
        self.collection = self.db["products"]

    async def create(self, product_model: ProductModel) -> bool:
        """
        Insere um novo produto no banco.
        """
        # Converte o modelo Pydantic para um dicionário
        result = await self.collection.insert_one(product_model.model_dump())

        # Retorna True se a inserção foi reconhecida pelo banco
        return result.acknowledged
