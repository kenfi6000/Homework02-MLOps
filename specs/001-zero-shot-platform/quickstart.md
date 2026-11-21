# Quickstart Validation

## Prerequisites
- Python 3.11+
- Docker with Docker Compose
- Network access to Hugging Face or populated model/cache files

## 1. Configure environment
Copy `.env.example` to `.env` and set placeholders. Never commit `.env`.

## 2. Start MinIO
Run `docker compose up -d minio`.
Open `http://localhost:9001` and verify that `zeroshot-learning-output` is created after application startup. The infrastructure implementation uses an S3-valid hyphenated name because modern MinIO rejects the underscore in `zeroshot_learning_output`.

## 3. Start Streamlit
Run `streamlit run app/streamlit_app.py`.

## 4. Validate model management
- Open the administrator page.
- Confirm DeBERTa and BART are configured.
- Download one model.
- Confirm it becomes ready and is not downloaded again unnecessarily.
- Delete it and confirm status becomes missing.

## 5. Validate classification
- Configure at least two labels.
- Select a ready model and label set.
- Submit representative text.
- Confirm predicted class, confidence, ranked scores, model, and timestamp.
- Verify the JSON object appears under `predictions/YYYY/MM/DD/` in MinIO.

## 6. Run tests
Run unit tests and integration tests as documented by the project. Integration tests should be skipped or clearly reported if MinIO is not running unless mocks are being used.
