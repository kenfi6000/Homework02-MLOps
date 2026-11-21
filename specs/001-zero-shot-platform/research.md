# Research

## Decision: Streamlit with service modules
**Rationale**: Streamlit satisfies the requested local web UI while service modules keep model, inference, and storage responsibilities independently testable.
**Alternatives considered**: FastAPI plus React was rejected as unnecessary complexity for the MVP.

## Decision: Hugging Face Transformers pipeline
**Rationale**: The `zero-shot-classification` pipeline directly supports the requested task and can load the primary and secondary models.
**Alternatives considered**: Direct token/model use would duplicate pipeline behavior and increase implementation risk.

## Decision: MinIO Python client
**Rationale**: A native Python client supports bucket creation and JSON object upload with a small dependency footprint.
**Alternatives considered**: boto3-compatible S3 API is viable but may require extra configuration; one client should be chosen and documented.

## Decision: Controlled local model directory plus Hugging Face cache
**Rationale**: `MODEL_DIR` provides an application-owned ready-model view, while `HF_HOME`/`TRANSFORMERS_CACHE` support standard cache lifecycle and cleanup.
**Alternatives considered**: Cache-only storage was rejected because status and deletion are harder to present consistently.

## Decision: YAML configuration for models and labels
**Rationale**: YAML is human-readable and easy to version without committing runtime state.
**Alternatives considered**: Database storage was rejected as oversized for local MVP needs.
