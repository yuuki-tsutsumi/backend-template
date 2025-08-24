FROM python:3.13-slim

WORKDIR /app

# ヘルスチェック用にcurlを追加。
RUN apt-get update && apt-get install -y \
    curl gcc build-essential libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY . .

CMD ["poetry", "run", "uvicorn", "app.router.main:app", "--host", "0.0.0.0", "--port", "80"]
