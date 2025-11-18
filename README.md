# TDD Store API - Solução de Projeto

Este repositório contém uma API RESTful completa para uma loja (Store API), construída do zero utilizando **Desenvolvimento Orientado a Testes (TDD)**. O projeto foi desenvolvido em Python com FastAPI, Pytest, Motor (para MongoDB assíncrono) e Pydantic.

O objetivo principal foi seguir o ciclo TDD (Red-Green-Refactor) para cada funcionalidade, desde a configuração inicial do projeto até à implementação dos *endpoints* CRUD e regras de negócio complexas.

## 🚀 Funcionalidades da API

A API implementa todas as operações CRUD (Create, Read, Update, Delete) para produtos:

* `POST /products/`: Cria um novo produto.
* `GET /products/`: Lista todos os produtos (com filtros).
* `GET /products/{uuid}`: Obtém um produto específico por ID.
* `PUT /products/{uuid}`: Atualiza um produto.
* `DELETE /products/{uuid}`: Apaga um produto.

## 🏆 Solução do "Desafio Final"

Além do CRUD básico, este projeto implementa as soluções para o "Desafio Final" proposto, tudo seguindo o TDD:

### 1. Tratamento de Erros (Create)

**O Desafio:** Mapear uma exceção de erro de inserção (ex: BD offline) e capturá-la no *controller* para dar uma resposta amigável.

**A Solução (Red-Green-Refactor):**
1.  **Red (Teste):** Criei um teste de controlador (`test_create_product_should_return_500_on_db_error`) que usa `pytest.monkeypatch` para simular que o `ProductUsecase.create()` levanta uma `DatabaseException`. O teste espera receber um `HTTP 500` com o JSON `{"detail": "Ocorreu um erro..."}`.
2.  **Green (Código):**
    * Defini uma exceção personalizada `store.core.exceptions.DatabaseException`.
    * No `ProductUsecase`, adicionei um `try...except PyMongoError` ao redor da chamada do repositório, que "re-levanta" (re-raises) a exceção como `DatabaseException`.
    * No *controller* `POST /products/`, adicionei um `try...except DatabaseException` que apanha o erro e retorna a `HTTPException(500, ...)` correta.
3.  **Refactor (Teste):** O teste passou, confirmando que a API está robusta contra falhas de escrita na base de dados.

### 2. Lógica de Atualização (`updated_at`)

**O Desafio:** Ao alterar um dado (ex: `price`), o `updated_at` deve ser atualizado automaticamente para a hora atual. No entanto, se o utilizador *enviar* um `updated_at` no *request*, esse valor manual deve ser usado.

**A Solução (Red-Green-Refactor):**
1.  **Red (Testes):** Criei dois testes:
    * `test_update_product_should_auto_update_updated_at`: Faz um `PUT` apenas com o `price` e verifica se o `new_updated_at > original_updated_at`.
    * `test_update_product_should_allow_manual_updated_at`: Faz um `PUT` com `price` *e* um `updated_at` ("2000-01-01") e verifica se o `new_updated_at` é exatamente "2000-01-01".
2.  **Green (Código):**
    * Adicionei o campo `updated_at: Optional[datetime]` ao *schema* `ProductUpdate`.
    * Toda a lógica foi implementada no `ProductUsecase.update()`:
        ```python
        # Em store/usecases/product.py
        
        async def update(self, uuid: UUID, body: ProductUpdate) -> ProductOut | None:
            # Se o utilizador NÃO enviou um updated_at, defina-o para agora.
            if body.updated_at is None:
                body.updated_at = datetime.now(timezone.utc)
            
            # Passe o body (com o updated_at manual ou automático) para o repositório
            product_model = await self.repository.update(uuid, body)
            
            # ... (resto da lógica) ...
        ```
    * Garanti que o `repository.update()` usa `model_dump(exclude_none=True)` para incluir o `updated_at` definido pelo *usecase*.
3.  **Refactor (Teste):** Os dois testes passaram, confirmando a lógica de negócio dupla.

### 3. Filtros de Preço (List)

**O Desafio:** Aplicar um filtro de preço na listagem `GET /products/` (ex: `price > 5000 and price < 8000`).

**A Solução (Red-Green-Refactor):**
1.  **Red (Teste):** Criei um teste (`test_list_products_should_filter_by_price`) que cria 4 produtos com preços variados (4000, 6000, 7500, 9000). O teste depois chama `GET /products/?price_min=5000&price_max=8000` e falha, verificando `assert len(response_data) == 4` (errado) em vez de `2` (correto).
2.  **Green (Código):** A implementação foi feita em todas as camadas:
    * **Controller (`GET /`):** Adicionei os *query parameters* `price_min: Optional[float] = None` e `price_max: Optional[float] = None` e passei-os para o *usecase*.
    * **Usecase (`list`):** Modifiquei o método `list()` para aceitar `price_min` e `price_max` e passá-los para o *repositório*.
    * **Repository (`list`):** O método `list()` agora constrói uma *query* de filtro dinâmica para o MongoDB, usando os operadores `$gt` (greater than) e `$lt` (less than).
        ```python
        # Em store/repositories/product.py
        
        async def list(self, price_min: Optional[float] = None, price_max: Optional[float] = None) -> List[ProductModel]:
            filter_query = {}
            price_filter = {}
            
            if price_min is not None:
                price_filter["$gt"] = price_min
            
            if price_max is not None:
                price_filter["$lt"] = price_max
                
            if price_filter:
                filter_query["price"] = price_filter

            # A query de filtro é usada no .find()
            products = [ProductModel(**item) async for item in self.collection.find(filter_query)]
            return products
        ```
3.  **Refactor (Teste):** O teste passou, confirmando que o filtro da base de dados está a funcionar corretamente através da API.

## 🛠️ Tecnologias Utilizadas

* **Python 3.11+**
* **FastAPI:** Para a criação da API assíncrona.
* **Pytest:** Para testes (incluindo `pytest-asyncio` para testes assíncronos).
* **Pydantic (V2):** Para validação de dados e configurações.
* **MongoDB (Atlas):** Base de dados NoSQL na nuvem.
* **Motor:** Driver assíncrono para o MongoDB.
* **Poetry:** Para gestão de dependências e ambientes virtuais.

## 🏁 Como Executar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone [URL-DO-SEU-REPOSITÓRIO]
    cd tdd-project-api-store
    ```

2.  **Instale as dependências:**
    ```bash
    poetry install
    ```

3.  **Configure o ambiente:**
    * Crie um ficheiro `.env` na raiz do projeto.
    * Adicione as suas variáveis de ambiente:
        ```.env
        MONGODB_URL="mongodb+srv://user:pass@seu-cluster.mongodb.net/"
        MONGODB_DB_NAME="store"
        MONGODB_DB_NAME_TEST="test_store"
        ```

4.  **Execute os testes (Opcional, mas recomendado):**
    ```bash
    poetry run pytest
    ```

5.  **Execute a aplicação:**
    ```bash
    poetry run uvicorn store.main:app --reload
    ```
    A API estará disponível em `http://127.0.0.1:8000/docs`.