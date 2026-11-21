# Feature Specification: Zero-Shot MLOps Platform

**Feature Branch**: `001-zero-shot-platform`
**Created**: 2026-11-21
**Status**: Draft
**Input**: Build a production-oriented zero-shot text classification platform using Streamlit, Hugging Face Transformers, and MinIO.

## User Scenarios & Testing

### User Story 1 - Manage Local Zero-Shot Models (Priority: P1)
An administrator views configured models, downloads a missing model, verifies availability, refreshes status, deletes a model, or clears the Hugging Face cache.

**Why this priority**: Classification cannot work until a model is available locally.
**Independent Test**: Configure at least two models and complete download, availability, refresh, deletion, and cache-cleanup actions without classification UI access.

**Acceptance Scenarios**:
1. **Given** a model is missing locally, **When** download starts, **Then** the system saves a complete model under the controlled model directory and reports ready or failure status.
2. **Given** a complete model exists locally, **When** download starts again, **Then** the system reuses it without unnecessary download work.
3. **Given** a downloaded model is selected, **When** the administrator deletes it, **Then** availability becomes missing and local model files are removed.

### User Story 2 - Configure Candidate Labels (Priority: P2)
An administrator creates a named label set, validates it, saves it, and selects it for classification.

**Why this priority**: Candidate labels define the classes inference can predict.
**Independent Test**: Add, remove, save, and select label sets without starting a model.

**Acceptance Scenarios**:
1. **Given** fewer than two labels or duplicate/empty entries, **When** saving is attempted, **Then** validation rejects the label set and explains the problem.
2. **Given** a valid saved label set, **When** it is selected, **Then** it is available to the classification page.

### User Story 3 - Classify Text and Persist the Result (Priority: P1)
A user enters text, selects an available model and label set, submits it, sees ranked predictions, and receives confirmation of MinIO persistence.

**Why this priority**: This is the primary end-to-end user outcome.
**Independent Test**: Submit valid text with a mocked classifier and running or mocked MinIO, then inspect returned prediction and stored JSON.

**Acceptance Scenarios**:
1. **Given** valid text and selections, **When** classification succeeds, **Then** the page shows the predicted class, confidence, ranked list, model, timestamp, and storage status.
2. **Given** no model or valid label set is available, **When** submission is attempted, **Then** the page displays an actionable error.
3. **Given** MinIO is unavailable, **When** local classification succeeds, **Then** the page reports persistence failure and does not claim success.

### Edge Cases
- Failed or incomplete model downloads must not be marked ready.
- Empty text and fewer than two candidate labels must be rejected.
- Duplicate labels must be rejected case-insensitively.
- Missing or invalid MinIO configuration must produce a clear startup or runtime error.

## Requirements

### Functional Requirements
- **FR-001**: The system MUST display at least two configured Hugging Face zero-shot models.
- **FR-002**: The administrator MUST be able to download, refresh, inspect, and delete local models.
- **FR-003**: The model manager MUST reuse complete local models and clean up incomplete failed downloads.
- **FR-004**: The administrator MUST be able to clear the Hugging Face cache.
- **FR-005**: The system MUST add, remove, save, validate, and select named candidate-label sets.
- **FR-006**: Candidate-label sets MUST contain at least two non-empty, unique labels.
- **FR-007**: The classifier MUST reject empty text and invalid label sets.
- **FR-008**: The classifier MUST return the highest-scoring label and ranked label scores.
- **FR-009**: The system MUST create the environment-configured bucket when missing. The default deployment uses `zeroshot-learning-output`; the homework name `zeroshot_learning_output` is not valid for modern S3/MinIO bucket naming and therefore is not used as the live default.
- **FR-010**: Every successful classification MUST store a JSON record at `predictions/YYYY/MM/DD/{request_id}.json`.
- **FR-011**: Stored records MUST contain request ID, input text, predicted class, confidence, candidate labels, ranked predictions, model identifier, revision when available, timestamp, application version, and optional session ID.
- **FR-012**: The system MUST use environment variables for MinIO, model paths, cache paths, and optional Hugging Face credentials.
- **FR-013**: The system MUST expose clear errors for missing models, invalid input, failed downloads, and MinIO failures.
- **FR-014**: The repository MUST include unit tests, MinIO integration tests or test doubles, Docker Compose support, CI validation, and README documentation.

### Key Entities
- **ModelConfiguration**: Model ID, display name, task, optional revision.
- **DownloadedModel**: Model ID, local path, revision, completeness state.
- **LabelSet**: Name and ordered, validated labels.
- **ClassificationRequest**: Request ID, input text, model ID, label set, timestamp.
- **PredictionResult**: Predicted class, confidence, ranked predictions, model/revision, latency, application version.

## Success Criteria

### Measurable Outcomes
- **SC-001**: The administrator can inspect, download, refresh, and delete both configured models.
- **SC-002**: A valid classification request displays its predicted class, confidence, and ranked scores.
- **SC-003**: 100% of successful classifications produce valid JSON in the configured bucket.
- **SC-004**: Invalid input and unavailable dependencies produce clear, non-secret-bearing errors.
- **SC-005**: Automated unit tests and applicable integration tests pass.

## Assumptions
- Docker Compose and sufficient local memory/disk are available for the demonstration.
- Hugging Face network access or a populated cache is available for real downloads.
- The initial administrator interface is trusted/local and does not implement authentication.
- Python 3.11 or later is the baseline runtime unless compatibility testing establishes another supported floor.
