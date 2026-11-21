import json

import pytest

from app.services.minio_storage import MinioStorage


class MockMinio:
    def __init__(self, exists=False):
        self.exists = exists
        self.make_calls = []
        self.put_calls = []

    def bucket_exists(self, bucket):
        return self.exists

    def make_bucket(self, bucket):
        self.make_calls.append(bucket)
        self.exists = True

    def put_object(self, bucket, object_name, data, length, content_type):
        self.put_calls.append(
            (bucket, object_name, data.read(), length, content_type)
        )


def prediction(request_id="6a6d6a85-9dbb-4f3e-9f89-5d8e4e8c1b2a"):
    return {
        "request_id": request_id,
        "timestamp": "2026-10-31T12:00:00Z",
        "input_text": "The team won.",
        "predicted_class": "sports",
        "confidence": 0.96,
        "candidate_labels": ["sports", "politics"],
        "ranked_predictions": [
            {"label": "sports", "score": 0.96},
            {"label": "politics", "score": 0.04},
        ],
        "model": "MoritzLaurer/deberta-v3-base-zeroshot-v2.0",
        "model_revision": "main",
        "application_version": "0.1.0",
    }


@pytest.fixture
def storage(monkeypatch):
    monkeypatch.setenv("MINIO_ENDPOINT", "localhost:9000")
    monkeypatch.setenv("MINIO_ACCESS_KEY", "test")
    monkeypatch.setenv("MINIO_SECRET_KEY", "test")
    monkeypatch.setenv("MINIO_BUCKET", "zeroshot-learning-output")
    mock = MockMinio()
    return MinioStorage(client=mock), mock


def test_bucket_is_created(storage):
    service, mock = storage
    service.ensure_bucket()
    assert mock.make_calls == ["zeroshot-learning-output"]


def test_result_serializes_as_valid_json():
    payload = MinioStorage.serialize_result(prediction())
    decoded = json.loads(payload)
    assert decoded["predicted_class"] == "sports"


def test_object_path_uses_date_and_request_id():
    path = MinioStorage.object_path(
        "6a6d6a85-9dbb-4f3e-9f89-5d8e4e8c1b2a",
        "2026-10-31T12:00:00Z",
    )
    assert path == "predictions/2026/10/31/6a6d6a85-9dbb-4f3e-9f89-5d8e4e8c1b2a.json"


def test_store_prediction_contains_required_fields(storage):
    service, mock = storage
    object_name = service.store_prediction(prediction())
    assert object_name.startswith("predictions/2026/10/31/")
    assert len(mock.put_calls) == 1
    payload = json.loads(mock.put_calls[0][2])
    assert payload["request_id"]
    assert payload["candidate_labels"]
    assert payload["model"]
