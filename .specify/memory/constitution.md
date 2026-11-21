# Homework02-MLOps Constitution

## Core Principles

### I. Reproducible MLOps
Use pinned dependencies, explicit environment configuration, and documented model identifiers/revisions. Downloaded model files and Hugging Face caches must never be committed.

### II. Separation of Concerns
Streamlit pages contain presentation logic only. Model lifecycle, inference, configuration, logging, and MinIO persistence remain separate services or utilities.

### III. Test-First and Integration Verification
Core model, classifier, configuration, and storage behavior requires unit tests. MinIO integration behavior requires integration tests or documented test doubles. Tests should avoid network model downloads whenever mocks or lightweight fixtures are sufficient.

### IV. Safe Model Lifecycle
Detect existing models, download only missing revisions, use a controlled local model directory, prevent partial downloads from appearing ready, support explicit deletion, and allow Hugging Face cache cleanup.

### V. Data Persistence and Traceability
Every successful classification creates one structured JSON object in the configured MinIO bucket with request identity, input, ranked outputs, model identity/revision, timestamp, application version, and optional session identity.

### VI. Security and Privacy
Credentials and environment-specific settings come from environment variables or secret management. Secrets are never committed or logged. The administrator interface is initially unauthenticated and is documented for local or trusted environments only.

### VII. Clear Error Handling and Observability
Invalid input, missing models, failed downloads, unavailable MinIO, and storage failures produce actionable user-facing messages. Logs contain useful metadata without credentials or unnecessary sensitive input.

## Scope and Constraints
The first release targets a local Streamlit application and Docker Compose MinIO deployment. It supports at least two configurable Hugging Face zero-shot models and persisted classification records. Authentication, production-scale API serving, prediction browsing, batch CSV classification, and model comparison are outside the initial scope.

## Quality Gates
Implementation must pass formatting/lint checks, unit tests, applicable integration tests, Docker Compose startup validation, acceptance scenarios, and secret/model-file exclusion checks.

## Governance
This constitution supersedes individual implementation preferences. Amendments require a dated change, updated rationale, and revalidation of the specification, plan, data model, tasks, and acceptance tests.

**Version**: 1.0.0 | **Ratified**: 2026-11-21 | **Last Amended**: 2026-11-21
