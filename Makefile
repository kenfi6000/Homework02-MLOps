.PHONY: install test lint start-minio stop-minio run

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

lint:
	python -m ruff check app tests

start-minio:
	docker compose up -d minio

stop-minio:
	docker compose down

run:
	streamlit run app/streamlit_app.py
