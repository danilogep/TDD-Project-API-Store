# Store API — construída por TDD

[![CI](https://github.com/danilogep/TDD-Project-API-Store/actions/workflows/ci.yml/badge.svg)](https://github.com/danilogep/TDD-Project-API-Store/actions/workflows/ci.yml)
[![Cobertura 100%](https://img.shields.io/badge/cobertura-100%25-brightgreen)](#cobertura)
[![Python 3.12 | 3.13](https://img.shields.io/badge/python-3.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![Licença MIT](https://img.shields.io/badge/licença-MIT-green)](LICENSE)

API REST de catálogo de produtos em FastAPI + MongoDB, escrita teste primeiro. O argumento do projeto não é o CRUD — é a disciplina. Então ela está no topo e é verificável:

```bash
poetry install && poetry run pytest
```

**Um comando. Sem configurar banco, sem `.env`, sem subir nada antes.** A suíte levanta um MongoDB descartável em container, roda os 33 testes e derruba o container no fim. Basta ter Docker no ambiente.

```
33 passed in 6.46s
TOTAL   173 stmts   0 miss   100%
```

Já tem um Mongo no ar? Então nem o container é preciso:

```bash
MONGODB_URL_TEST=mongodb://localhost:27017 poetry run pytest
```

---

## O ciclo, num caso concreto

O desafio: ao alterar o preço de um produto, `updated_at` deve ser carimbado com a hora atual — **mas**, se o cliente mandar um `updated_at` explícito no corpo, o valor dele é que vale.

### 🔴 Red — o teste primeiro, falhando

```python
# tests/controllers/test_product_controller.py
async def test_update_product_should_auto_update_updated_at(client):
    response_post = await client.post("/products/", json=payload)
    product_uuid = response_post.json()["uuid"]
    original_updated_at = datetime.fromisoformat(response_post.json()["updated_at"])

    await asyncio.sleep(0.001)

    response_put = await client.put(f"/products/{product_uuid}", json={"price": 7500.00})

    new_updated_at = datetime.fromisoformat(response_put.json()["updated_at"])
    assert new_updated_at > original_updated_at
```

```
>       assert new_updated_at > original_updated_at
E       assert datetime.datetime(2026, 10, 8, 19, 33, 40, 948000, tzinfo=datetime.timezone.utc)
E            > datetime.datetime(2026, 10, 8, 19, 33, 40, 948257, tzinfo=datetime.timezone.utc)
FAILED tests/controllers/test_product_controller.py::test_update_product_should_auto_update_updated_at
1 failed in 1.07s
```

A diferença de 257 microssegundos entre os dois lados é só o arredondamento do
BSON para milissegundos — o `updated_at` gravado é o mesmo do `POST`. É esse o
sinal do vermelho: a atualização não recarimbou nada.

Falha porque `ProductUpdate` não tinha `updated_at` e nada recarimbava o campo: o `$set` gravava só o preço.

### 🟢 Green — o mínimo para passar

```python
# store/usecases/product.py
async def update(self, uuid: UUID, body: ProductUpdate) -> ProductOut | None:
    # Carimba só quando o cliente não mandou valor próprio. É esta única
    # linha que separa "atualizado agora" de "atualizado quando eu disser".
    if body.updated_at is None:
        body.updated_at = datetime.now(UTC)

    product_model = await self.repository.update(uuid, body)
    ...
```

```python
# store/repositories/product.py — exclude_none é o que faz a regra funcionar:
# campo não enviado não vira $set, e não apaga o que está gravado.
update_data = product_update.model_dump(exclude_none=True)
```

### 🔵 Refactor — e o segundo teste, que trava a outra metade

Com o automático verde, o manual entra como teste próprio, para que uma simplificação futura não derrube a regra:

```python
async def test_update_product_should_allow_manual_updated_at(client):
    update_payload = {"price": 7500.00, "updated_at": "2000-01-01T00:00:00+00:00"}
    response_put = await client.put(f"/products/{product_uuid}", json=update_payload)

    assert datetime.fromisoformat(response_put.json()["updated_at"]) == manual_date
```

Os dois vivem lado a lado em [`tests/controllers/test_product_controller.py`](tests/controllers/test_product_controller.py).

---

## Cobertura

```
Name                             Stmts   Miss  Cover
-----------------------------------------------------
store/controllers/product.py        41      0   100%
store/core/config.py                 7      0   100%
store/core/db.py                    12      0   100%
store/core/exceptions.py             4      0   100%
store/main.py                        7      0   100%
store/models/product.py              8      0   100%
store/repositories/product.py       39      0   100%
store/schemas/product.py            23      0   100%
store/usecases/product.py           35      0   100%
-----------------------------------------------------
TOTAL                              173      0   100%
```

O número não veio de cobrir o caminho feliz com mais asserções. Veio de [`tests/test_caminhos_de_erro.py`](tests/test_caminhos_de_erro.py), que trava o que ninguém exercita à mão: `PUT` e `DELETE` em UUID inexistente, UUID malformado na rota, `update` sem documento correspondente, e a falha do driver virando `DatabaseException`.

O CI reprova abaixo de 90%.

---

## Por que um Mongo de verdade nos testes

Quase tudo que esta API faz é tradução entre Pydantic e BSON: UUID nativo, `datetime` com fuso, `$gt`/`$lt`/`$set`. Um dobro em memória concorda com qualquer coisa que o repositório mande — e passaria verde exatamente nos pontos em que o banco reprovaria. Então a suíte fala com um MongoDB real, e o custo disso foi empurrado para a infraestrutura em vez do desenvolvedor:

| Como você roda | O que acontece |
|---|---|
| `poetry run pytest` | [testcontainers](https://testcontainers.com/) sobe um `mongo:7`, roda, derruba |
| `MONGODB_URL_TEST=... pytest` | usa o servidor que você indicou |
| CI | usa o serviço `mongo:7.0` do GitHub Actions |

A variável `MONGODB_URL` — a do banco da aplicação — **nunca** é usada pelos testes. Teste que executa `drop_collection` não escolhe sozinho em qual servidor vai fazer isso.

---

## A API

| Método | Rota | O que faz |
|---|---|---|
| `POST` | `/products/` | Cria um produto |
| `GET` | `/products/` | Lista, com `price_min` e `price_max` opcionais |
| `GET` | `/products/{uuid}` | Consulta por ID |
| `PUT` | `/products/{uuid}` | Atualiza (com a regra de `updated_at`) |
| `DELETE` | `/products/{uuid}` | Remove |
| `GET` | `/healthcheck` | Disponibilidade |

Subindo a aplicação:

```bash
cp .env.example .env
docker compose up --build       # API em localhost:8000/docs, Mongo em 27017
```

<details>
<summary>Sem Docker</summary>

```bash
poetry install
cp .env.example .env            # aponte MONGODB_URL para o seu Mongo
poetry run uvicorn store.main:app --reload
```
</details>

---

## Os outros dois desafios

**Tratamento de erro na escrita.** O `ProductUsecase` captura `PyMongoError` e relança como `DatabaseException`; o controller traduz para `HTTP 500` com mensagem própria. A camada de cima não precisa saber qual banco existe lá embaixo — e o cliente não recebe detalhe de infraestrutura na resposta. Travado por `test_create_product_should_return_500_on_db_error` e `test_falha_do_banco_vira_database_exception`.

**Filtro de preço.** `GET /products/?price_min=5000&price_max=8000` desce pelas três camadas até virar `{"price": {"$gt": 5000, "$lt": 8000}}` no `find`. O teste cria quatro produtos de preços distintos e exige que voltem exatamente dois.

---

## Arquitetura

```
store/controllers/   rotas HTTP, tradução de exceção para status code
store/usecases/      regra de negócio; não conhece HTTP nem PyMongo
store/repositories/  acesso ao MongoDB; não conhece regra de negócio
store/schemas/       contrato de entrada e saída (Pydantic)
store/models/        documento como é gravado
store/core/          configuração, conexão e exceções
```

Cada camada é testada no seu nível: repositório contra banco real, usecase com repositório dublado, controller ponta a ponta.

## Stack

FastAPI · Pydantic v2 · Motor (MongoDB assíncrono) · Poetry · pytest · pytest-asyncio · testcontainers · ruff · pre-commit

## Qualidade

```bash
poetry run ruff check .          # lint
poetry run pre-commit install    # roda ruff + checagens a cada commit
```

As mesmas verificações rodam no CI, em Python 3.12 e 3.13.

## Licença

[MIT](LICENSE).
