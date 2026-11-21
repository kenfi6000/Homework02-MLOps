import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MINIO_INTEGRATION") != "1",
    reason="Set RUN_MINIO_INTEGRATION=1 when MinIO is running",
)


def test_live_minio_bucket_and_object(monkeypatch):
    monkeypatch.setenv("MINIO_ENDPOINT", os.getenv("MINIO_ENDPOINT", "localhost:9000"))
    monkeypatch.setenv("MINIO_ACCESS_KEY", os.getenv("MINIO_ACCESS_KEY", "minioadmin"))
    monkeypatch.setenv("MINIO_SECRET_KEY", os.getenv("MINIO_SECRET_KEY", "minioadmin"))
    monkeypatch.setenv("MINIO_SECURE", "false")
    monkeypatch.setenv("MINIO_BUCKET", "zeroshot-learning-output")

    from app.services.minio_storage import MinioStorage

    storage = MinioStorage()
    storage.ensure_bucket()
    assert storage.client.bucket_exists(storage.bucket)
