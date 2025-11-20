# Makefile for ForgeAI backend

.PHONY: install test lint format clean run migrate

install:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

lint:
	flake8 app/ tests/
	mypy app/

format:
	black app/ tests/
	isort app/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(message)"

