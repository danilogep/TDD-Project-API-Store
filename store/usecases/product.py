from datetime import UTC, datetime
from uuid import UUID

from pymongo.errors import PyMongoError

from store.core.exceptions import DatabaseException
from store.models.product import ProductModel
from store.repositories.product import ProductRepository
from store.schemas.product import ProductIn, ProductOut, ProductUpdate


class ProductUsecase:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def create(self, body: ProductIn) -> ProductOut:
        """
        Coordena a criação de um novo produto.
        """
        product_model = ProductModel(**body.model_dump())

        try:
            await self.repository.create(product_model)
        except PyMongoError as erro:
            raise DatabaseException(f"Erro ao inserir produto no banco: {erro}") from erro

        product_out = ProductOut(**product_model.model_dump())

        return product_out

    # 2. MÉTODO 'LIST'
    async def list(
        self, price_min: float | None = None, price_max: float | None = None
    ) -> list[ProductOut]:
        """
        Coordena a listagem de produtos, aplicando filtros.
        """
        # 3. Passa os filtros para o repositório
        products_model = await self.repository.list(
            price_min=price_min, price_max=price_max
        )

        return [ProductOut(**product.model_dump()) for product in products_model]

    async def get(self, uuid: UUID) -> ProductOut | None:
        """
        Coordena a busca de um produto.
        """
        product_model = await self.repository.get(uuid)

        if not product_model:
            return None

        return ProductOut(**product_model.model_dump())

    async def update(self, uuid: UUID, body: ProductUpdate) -> ProductOut | None:
        """
        Coordena a atualização de um produto.
        """
        if body.updated_at is None:
            body.updated_at = datetime.now(UTC)

        product_model = await self.repository.update(uuid, body)

        if not product_model:
            return None

        return ProductOut(**product_model.model_dump())

    async def delete(self, uuid: UUID) -> bool:
        """
        Coordena a exclusão de um produto.
        """
        return await self.repository.delete(uuid)
