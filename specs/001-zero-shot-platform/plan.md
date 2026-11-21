# Implementation Plan: Zero-Shot MLOps Platform

**Branch**: `001-zero-shot-platform`
**Date**: 2026-11-21
**Spec**: [spec.md](./spec.md)

## Summary
Create a Streamlit application that separates model lifecycle, candidate-label configuration, zero-shot inference, and MinIO persistence. Ship Docker Compose MinIO support, environment-based configuration, unit/integration tests, CI, and developer documentation.

## Technical Context
- **Language/Version**: Python 3.11+
- **Primary Dependencies**: Streamlit, Hugging Face Transformers, PyTorch, PyYAML, boto3 or minio-py
- **Storage**: Local model/cache directories and JSON objects in MinIO
- **Testing**: pytest, pytest-mock where needed
- **Target Platform**: Docker Compose on Windows/Linux/macOS
- **Project Type**: Local web application
- **Performance Goals**: Initial MVP is correctness-oriented; avoid loading multiple models simultaneously
- **Constraints**: Large model downloads require disk/network, credentials stay in environment variables
- **Scale/Scope**: Local/trusted users and a single application process

## Constitution Check
- PASS: Reproducible dependencies and environment configuration are planned.
- PASS: UI and services are separated.
- PASS: Unit/integration testing and CI are planned.
- PASS: Model lifecycle and safe cache handling are designed.
- PASS: Successful results are persisted as structured JSON.
- PASS: Secrets are excluded and security limitations documented.
- PASS: README and troubleshooting documentation are planned.

## Project Structure

```text
zeroshot-mlops/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── configs/
│   ├── models.yaml
│   └── labels.yaml
├── app/
│   ├── streamlit_app.py
│   ├── pages/
│   │   ├── 1_Admin.py
│   │   └── 2_Classify_Text.py
│   ├── services/
│   │   ├── model_manager.py
│   │   ├── classifier.py
│   │   └── minio_storage.py
│   └── utils/
│       ├── config.py
│       └── logging_config.py
├── models/
│   └── .gitkeep
├── tests/
│   ├── test_model_manager.py
│   ├── test_classifier.py
│   └── test_minio_storage.py
├── .specify/
├── specs/001-zero-shot-platform/
│   ├── spec.md
│   ├── plan.md
│   ├── research.md
│   ├── data-model.md
│   ├── quickstart.md
│   ├── contracts/
│   └── tasks.md
└── .github/workflows/ci.yml
```

**Structure Decision**: Use a small modular Streamlit repository. The plan avoids a backend API because the homework scope is a local web application.

## Complexity Tracking
No constitution violations require exception approval.
