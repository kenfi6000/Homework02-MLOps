# Data Model

## ModelConfiguration
- `id`: exact Hugging Face model identifier
- `name`: display name
- `task`: must be `zero-shot-classification`
- `revision`: optional revision or tag
- Validation: unique ID and non-empty fields

## DownloadedModel
- `model_id`: exact configured model ID
- `local_path`: path beneath configured `MODEL_DIR`
- `revision`: resolved revision when available
- `status`: `missing`, `downloading`, `ready`, or `failed`
- Transition: `missing -> downloading -> ready|failed`; ready/failed -> missing after deletion or cleanup

## LabelSet
- `name`: unique, non-empty name
- `labels`: ordered list of non-empty unique strings
- Validation: at least two labels, case-insensitive uniqueness

## ClassificationRequest
- `request_id`: UUID
- `input_text`: trimmed non-empty text
- `model_id`: configured model identifier
- `label_set_name`: saved label set name
- `timestamp`: UTC ISO-8601 timestamp

## PredictionResult
- `predicted_class`: highest-scoring label
- `confidence`: score for predicted class
- `ranked_predictions`: ordered label/score objects
- `model_revision`: resolved revision when available
- `latency_ms`: optional inference latency
- `application_version`: application version string
