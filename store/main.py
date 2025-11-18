from fastapi import FastAPI

# 1. Importe o router do produto
from store.controllers.product import router as product_router

app = FastAPI(title="Store API")


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


# 2. Inclua o router na sua aplicação, com um prefixo
app.include_router(product_router, prefix="/products", tags=["products"])
