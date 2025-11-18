from motor.motor_asyncio import AsyncIOMotorDatabase
from store.models.product import ProductModel
from store.schemas.product import ProductUpdate
from store.core.db import mongo_client
from typing import List, Optional
from uuid import UUID
from pymongo.results import UpdateResult, DeleteResult


class ProductRepository:
    def __init__(self, db_client: AsyncIOMotorDatabase = None):
        self.db = db_client if db_client is not None else mongo_client.get_database()
        self.collection = self.db["products"]

    async def create(self, product_model: ProductModel) -> bool:
        result = await self.collection.insert_one(product_model.model_dump())
        return result.acknowledged

    # 2. MÉTODO 'LIST'
    async def list(
        self, price_min: Optional[float] = None, price_max: Optional[float] = None
    ) -> List[ProductModel]:
        """
        Lista produtos, opcionalmente filtrando por preço.
        """
        # 3. Constroi a query de filtro
        filter_query = {}
        price_filter = {}

        if price_min is not None:
            price_filter["$gt"] = price_min  # "greater than"

        if price_max is not None:
            price_filter["$lt"] = price_max  # "less than"

        if price_filter:
            filter_query["price"] = price_filter

        # 4. Usa a query de filtro no 'find'
        products = [
            ProductModel(**item) async for item in self.collection.find(filter_query)
        ]
        return products

    async def get(self, uuid: UUID) -> ProductModel | None:
        """
        Busca um produto pelo UUID.
        """
        product_data = await self.collection.find_one({"uuid": uuid})

        if product_data:
            return ProductModel(**product_data)
        return None

    async def update(
        self, uuid: UUID, product_update: ProductUpdate
    ) -> ProductModel | None:
        """
        Atualiza um produto pelo UUID.
        """
        update_data = product_update.model_dump(exclude_none=True)

        result: UpdateResult = await self.collection.update_one(
            {"uuid": uuid}, {"$set": update_data}
        )

        if result.modified_count > 0:
            return await self.get(uuid)

        return None

    async def delete(self, uuid: UUID) -> bool:
        """
        Apaga um produto pelo UUID.
        """
        result: DeleteResult = await self.collection.delete_one({"uuid": uuid})
        return result.deleted_count > 0
