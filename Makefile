.PHONY: up down restart logs enter build alembic_history alembic_head alembic_autogenerate alembic_downgrade pyenv-init install-python install-poetry setup clean re-setup

# Docker
up:
	docker-compose up -d
	make alembic_head

down:
	docker-compose down

build:
	docker-compose build --no-cache

restart:
	make down
	make up

logs:
	docker-compose logs -f

enter:
	docker container exec -it product-name-backend bash

enter-db:
	docker container exec -it product-name-db bash

test:
	docker-compose exec backend pytest tests

test-v:
	docker-compose exec backend pytest tests -vv

# Usage:
# make test-specific test=tests/test_example.py
# or
# make test-specific test=tests/test_example.py::TestClass::test_method
test-specific:
	docker-compose exec backend pytest $(test)

test-specific-v:
	docker-compose exec backend pytest $(test) -vv



# Alembic
alembic_history:
	docker-compose exec backend alembic -c alembic.ini history --verbose

alembic_head:
	docker-compose exec backend alembic -c alembic.ini upgrade head

alembic_autogenerate:
	@read -p "Enter the name of the migration file: " filename; \
	docker-compose exec backend alembic -c alembic.ini revision --autogenerate -m "$$filename"

alembic_downgrade:
	docker-compose exec backend alembic -c alembic.ini downgrade -1

mypy:
	docker-compose exec backend mypy . --strict

init-data:
	docker-compose exec backend env PYTHONPATH=/app python scripts/init_data.py

init-template:
	docker-compose exec backend env PYTHONPATH=/app python scripts/init_template.py

# 初期構築
PYTHON_VERSION = 3.13.3

POETRY_ENV = $(shell poetry env info --path 2>/dev/null)

PYTHON_BIN := $(shell pyenv which python 2>/dev/null || echo python3)

pyenv-init:
	@echo "Initializing pyenv..."
	@eval "$(pyenv init --path)"
	@eval "$(pyenv init -)"

install-python: pyenv-init
	@echo "Installing Python $(PYTHON_VERSION) with pyenv..."
	@pyenv install -s $(PYTHON_VERSION)
	@pyenv local $(PYTHON_VERSION)

install-poetry:
	@echo "Installing Poetry..."
	@pip install --upgrade poetry

setup: install-python install-poetry
	@if [ -z "$(POETRY_ENV)" ]; then \
		echo "Creating Poetry environment..."; \
		eval "$$(pyenv init --path)"; \
		eval "$$(pyenv init -)"; \
		poetry env use "$$(pyenv which python)"; \
	fi
	@echo "Installing dependencies..."
	@poetry install

clean:
	@echo "Removing Poetry environment..."
	@if [ -d "$$(poetry env info -p 2>/dev/null)" ]; then \
		rm -rf "$$(poetry env info -p 2>/dev/null)"; \
		echo "Poetry environment removed."; \
	else \
		echo "Poetry environment does not exist."; \
	fi

re-setup: clean setup
