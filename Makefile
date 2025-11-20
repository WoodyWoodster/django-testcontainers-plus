.PHONY: help format lint typecheck test coverage check clean install

help:
	@echo "Django Testcontainers Plus - Development Commands"
	@echo ""
	@echo "  make install    - Install all dependencies with uv"
	@echo "  make format     - Auto-format code with ruff"
	@echo "  make lint       - Run ruff linting"
	@echo "  make typecheck  - Run mypy type checking"
	@echo "  make test       - Run pytest tests"
	@echo "  make coverage   - Run tests with coverage report"
	@echo "  make check      - Run all checks (format, lint, typecheck, test)"
	@echo "  make clean      - Remove generated files"
	@echo ""

install:
	uv sync --all-extras --dev

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

typecheck:
	uv run mypy src/

test:
	uv run pytest tests/ -v

coverage:
	uv run pytest tests/ -v --cov=django_testcontainers_plus --cov-report=html --cov-report=term --cov-report=xml

check: lint typecheck test
	@echo "✅ All checks passed!"

clean:
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
