from fastapi import APIRouter, status, Depends, HTTPException, Response
from store.schemas.product import ProductIn, ProductOut, ProductUpdate
from store.usecases.product import ProductUsecase
from store.repositories.product import ProductRepository
from store.core.db import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from uuid import UUID
from store.core.exceptions import DatabaseException

router = APIRouter()


def get_repository(db: AsyncIOMotorDatabase = Depends(get_db)):
    return ProductRepository(db_client=db)


def get_usecase(repo: ProductRepository = Depends(get_repository)):
    return ProductUsecase(repository=repo)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductOut)
async def post(body: ProductIn, usecase: ProductUsecase = Depends(get_usecase)):
    try:
        return await usecase.create(body=body)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao inserir o produto.",
        )


# 2. MÉTODO 'GET'
@router.get("/", status_code=status.HTTP_200_OK, response_model=List[ProductOut])
async def get(
    # 3. Adiciona os query parameters (opcionais)
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    usecase: ProductUsecase = Depends(get_usecase),
):
    """
    Endpoint para listar todos os produtos (com filtros de preço).
    """
    # 4. Passe os filtros para o usecase
    return await usecase.list(price_min=price_min, price_max=price_max)


@router.get("/{uuid}", status_code=status.HTTP_200_OK, response_model=ProductOut)
async def get_one(uuid: UUID, usecase: ProductUsecase = Depends(get_usecase)):
    """
    Endpoint para buscar um produto por UUID.
    """
    product = await usecase.get(uuid=uuid)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto não encontrado com o uuid: {uuid}",
        )

    return product


@router.put("/{uuid}", status_code=status.HTTP_200_OK, response_model=ProductOut)
async def put(
    uuid: UUID, body: ProductUpdate, usecase: ProductUsecase = Depends(get_usecase)
):
    """
    Endpoint para atualizar um produto por UUID.
    """
    product = await usecase.update(uuid=uuid, body=body)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto não encontrado com o uuid: {uuid}",
        )

    return product


@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(uuid: UUID, usecase: ProductUsecase = Depends(get_usecase)):
    """
    Endpoint para apagar um produto por UUID.
    """
    deleted = await usecase.delete(uuid=uuid)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto não encontrado com o uuid: {uuid}",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
