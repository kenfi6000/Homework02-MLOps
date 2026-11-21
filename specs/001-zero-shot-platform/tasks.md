# Tasks: Zero-Shot MLOps Platform

**Input**: Design documents from `/specs/001-zero-shot-platform/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup

- [X] T001 Create the recommended Python project structure in [zeroshot-mlops/](../../)
- [X] T002 Add pinned/runtime dependencies in `pyproject.toml` and `requirements.txt`
- [X] T003 [P] Add `.env.example`, root `.gitignore`, and placeholder-safe model/cache directories
- [X] T004 [P] Configure formatting and lint commands for the project

## Phase 2: Foundational Infrastructure

- [X] T005 Implement environment and YAML configuration loading in `app/utils/config.py`
- [X] T006 [P] Implement structured logging in `app/utils/logging_config.py`
- [X] T007 Create initial model configuration with DeBERTa and BART in `configs/models.yaml`
- [X] T008 Create an initial default candidate-label set in `configs/labels.yaml`
- [X] T009 Implement shared validation helpers for text and candidate labels
- [X] T010 Implement Docker Compose MinIO configuration in `docker-compose.yml`
- [X] T011 Add base application entry point in `app/streamlit_app.py`

**Checkpoint**: Foundation ready for independent user stories.

## Phase 3: User Story 1 - Model Management (P1)

### Tests
- [X] T012 [P] [US1] Add model configuration, availability, path-safety, deletion, and cache-cleanup tests in `tests/test_model_manager.py`
- [X] T013 [P] [US1] Add mock-based failed-download and partial-download cleanup tests

### Implementation
- [X] T014 [US1] Implement model configuration loading and local path generation in `app/services/model_manager.py`
- [X] T015 [US1] Implement Hugging Face download, completeness detection, and revision reporting
- [X] T016 [US1] Implement safe model deletion and Hugging Face cache cleanup
- [X] T017 [US1] Build the administrator model-management UI in `app/pages/1_Admin.py`

**Checkpoint**: Both configured models can be inspected, downloaded, refreshed, and deleted safely.

## Phase 4: User Story 2 - Candidate Labels (P2)

### Tests
- [X] T018 [P] [US2] Add label validation, duplicate prevention, and persistence tests

### Implementation
- [X] T019 [US2] Implement label-set loading and saving in `app/utils/config.py`
- [X] T020 [US2] Add label add/remove/save/select controls to `app/pages/1_Admin.py`

**Checkpoint**: Valid named label sets can be created and selected.

## Phase 5: User Story 3 - Classification and MinIO Persistence (P1)

### Tests
- [X] T021 [P] [US3] Add valid/empty text and candidate-label tests in `tests/test_classifier.py`
- [X] T022 [P] [US3] Add ranking and highest-score tests using a mocked pipeline
- [X] T023 [P] [US3] Add bucket, JSON serialization, object path, and required-field tests in `tests/test_minio_storage.py`
- [X] T024 [P] [US3] Add MinIO integration tests that require a running service

### Implementation
- [X] T025 [US3] Implement pipeline initialization and cached zero-shot inference in `app/services/classifier.py`
- [X] T026 [US3] Implement MinIO bucket creation and JSON upload in `app/services/minio_storage.py`
- [X] T027 [US3] Implement unique request IDs, UTC timestamps, revision capture, and date-based object paths
- [X] T028 [US3] Build text input, model/label selection, ranked results, and error UI in `app/pages/2_Classify_Text.py`
- [X] T029 [US3] Wire successful predictions to MinIO and prevent false persistence success

**Checkpoint**: Valid classification produces ranked output and a complete JSON object in MinIO.

## Phase 6: Deployment and Documentation

- [X] T030 Add `Dockerfile` and complete MinIO Compose startup/volume configuration
- [X] T031 Add `.github/workflows/ci.yml` with dependency, lint, and test validation
- [X] T032 Add unit/integration test commands and fixtures to `Makefile`
- [X] T033 Write complete setup, architecture, usage, MinIO, test, and troubleshooting documentation in `README.md`
- [X] T034 Document model/cache behavior, security limitations, and environment configuration
- [X] T035 Add project version handling and expose it in prediction records

## Phase 7: Validation

- [X] T036 Run formatting, linting, and unit tests
- [X] T037 Start MinIO through Docker Compose and run integration tests
- [ ] T038 Demonstrate both model statuses and one real or representative classification
- [X] T039 Verify the stored prediction against [prediction-record.json](contracts/prediction-record.json)
- [X] T040 Run acceptance checks and remove any secrets, model files, and runtime caches from Git status

## Dependencies

- Phase 2 blocks all user-story implementation.
- US1 and US2 are independently usable after Phase 2.
- US3 depends on US1 for model availability and US2 for label-set selection.
- Deployment and documentation depend on working service implementations.

## Parallel Opportunities

- T003/T004 and T006/T007 can proceed independently during setup.
- T012/T013, T018, T021/T022/T023/T024 can be developed as independent test tasks.
- T017 and T020 should share services but can be implemented after those services.
- T030/T031/T032/T033 can proceed after core behavior is known.

## MVP Scope

The MVP is complete after Phase 5: model management, valid label configuration, classification, and MinIO persistence work with local or mocked dependencies. Phases 6 and 7 are required before submission.
