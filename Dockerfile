FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --no-cache-dir "poetry>=2.0,<3.0"

# O lock vem antes do código: mexer num controller não reinstala tudo.
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction

# O README entra porque o pyproject o declara: sem ele, `poetry install`
# da raiz falha com "Readme path /app/README.md does not exist".
COPY README.md ./
COPY store ./store
RUN poetry install --only-root --no-interaction

EXPOSE 8000

CMD ["uvicorn", "store.main:app", "--host", "0.0.0.0", "--port", "8000"]
