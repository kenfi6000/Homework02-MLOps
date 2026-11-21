# Zero-Shot MLOps Platform

This project is a local Streamlit application for Hugging Face zero-shot text classification. It provides model management, candidate-label configuration, ranked inference, and JSON prediction persistence in MinIO.

## Architecture

- `app/streamlit_app.py`: Streamlit landing page.
- `app/pages/1_Admin.py`: model and label administration.
- `app/pages/2_Classify_Text.py`: text classification UI.
- `app/services/model_manager.py`: model discovery, download, deletion, and cache cleanup.
- `app/services/classifier.py`: cached Hugging Face pipelines and inference.
- `app/services/minio_storage.py`: bucket creation and JSON object storage.
- `app/utils/config.py`: environment and YAML configuration.
- `configs/models.yaml`: supported Hugging Face models.
- `configs/labels.yaml`: persisted label sets.

## Supported models

- `MoritzLaurer/deberta-v3-base-zeroshot-v2.0`
- `facebook/bart-large-mnli`

Additional models can be added to `configs/models.yaml` when they use the `zero-shot-classification` task.

## Prerequisites

- Python 3.11+
- Docker Desktop with Docker Compose
- Network access to Hugging Face for real model downloads
- Sufficient disk/memory for model files

## Setup

```powershell
Copy-Item .env.example .env
python -m pip install -e ".[dev]"
```

Environment variables:

| Variable | Purpose | Default |
|---|---|---|
| `MINIO_ENDPOINT` | MinIO API endpoint | `localhost:9000` |
| `MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO secret key | `minioadmin` |
| `MINIO_SECURE` | HTTPS mode | `false` |
| `MINIO_BUCKET` | Prediction bucket | `zeroshot-learning-output` |
| `MODEL_DIR` | Downloaded model root | `./models` |
| `HF_HOME` | Hugging Face cache root | `./.cache/huggingface` |
| `TRANSFORMERS_CACHE` | Transformers cache root | `./.cache/huggingface/transformers` |
| `HF_TOKEN` | Optional Hugging Face token | empty |
| `APP_VERSION` | Stored application version | `0.1.0` |

Never commit `.env`, Hugging Face tokens, model files, or cache directories.

## Start MinIO

```powershell
docker compose up -d minio
```

Open `http://localhost:9001`. Default development credentials are `minioadmin` / `minioadmin`.

## Start Streamlit

```powershell
streamlit run app/streamlit_app.py
```

Open `http://localhost:8501`.

## Download and use models

1. Open the **Administrator** page.
2. Confirm both configured models.
3. Select **Download** for DeBERTa or BART.
4. Wait until status becomes `ready`.
5. Add or select at least two candidate labels and save the set.
6. Open **2_Classify_Text**.
7. Enter text, select a downloaded model and label set, then select **Classify**.

Model readiness is reused on repeated downloads. Downloads use a staging directory and are promoted to the local model directory only after `config.json` and weights are present. Failed or partial downloads are removed.

## MinIO verification

After a successful classification, open `zeroshot-learning-output` in the MinIO console. Objects are stored at:

```text
predictions/YYYY/MM/DD/{request_id}.json
```

Each JSON object contains the request ID, input, predicted class, confidence, candidate labels, ranked predictions, model ID/revision, timestamp, application version, and optional latency.

## Model deletion and cache cleanup

Use **Delete** on the Administrator page to remove one downloaded model. Use **Clear Hugging Face cache** to remove the configured Hugging Face cache. Both operations require explicit administrator action.

## Tests

```powershell
python -m pytest -q
python -m ruff check app tests
```

Unit tests use mocks and do not download large models. To run live MinIO integration tests:

```powershell
$env:RUN_MINIO_INTEGRATION="1"
docker compose up -d minio
python -m pytest tests/test_minio_integration.py -q
Remove-Item Env:RUN_MINIO_INTEGRATION
```

## Docker

```powershell
docker compose up --build
```

Stop services:

```powershell
docker compose down
```

## Troubleshooting

- **Model remains missing**: confirm network access and Hugging Face credentials, then inspect the Streamlit error.
- **CUDA or memory error**: use a smaller model or a machine with more memory; the MVP uses the CPU pipeline if no GPU setup is available.
- **MinIO connection refused**: run `docker compose up -d minio` and verify port `9000`.
- **Invalid or missing credentials**: copy `.env.example` to `.env` and set matching values.
- **Labels rejected**: provide at least two non-empty, case-insensitively unique labels.
- **Docker container cannot find `.env`**: the Compose file intentionally allows `.env` to be optional.

## Security limitation

The initial administrator page has no authentication. It is intended only for local development or a trusted environment. Do not expose it publicly without adding authentication and network controls.
