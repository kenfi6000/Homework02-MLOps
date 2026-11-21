import io
import json
import re
from datetime import datetime, timezone
from typing import Any

from minio import Minio

from app.utils.config import env
from app.utils.logging_config import configure_logging

logger = configure_logging()


class MinioStorage:
    def __init__(self, client: Minio | None = None) -> None:
        endpoint = env("MINIO_ENDPOINT", "localhost:9000")
        access_key = env("MINIO_ACCESS_KEY", "")
        secret_key = env("MINIO_SECRET_KEY", "")
        secure = env("MINIO_SECURE", "false").lower() == "true"
        self.bucket = env("MINIO_BUCKET", "zeroshot-learning-output")
        if not endpoint or not access_key or not secret_key:
            raise ValueError("MINIO_ENDPOINT, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY are required")
        if not re.fullmatch(r"(?=.{3,63}$)(?!-)(?!.*--)[a-z0-9][a-z0-9.-]*[a-z0-9]", self.bucket):
            raise ValueError(
                f"MINIO_BUCKET '{self.bucket}' is not valid for S3/MinIO "
                "(use lowercase letters, numbers, dots, or hyphens)"
            )
        self.client = client or Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def ensure_bucket(self) -> None:
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
            logger.info("MinIO bucket is available", extra={"bucket": self.bucket})
        except Exception as exc:
            raise RuntimeError(f"Could not initialize MinIO bucket '{self.bucket}': {exc}") from exc

    @staticmethod
    def serialize_result(result: dict[str, Any]) -> bytes:
        return json.dumps(result, indent=2, sort_keys=False).encode("utf-8")

    @staticmethod
    def object_path(request_id: str, timestamp: str | None = None) -> str:
        if timestamp:
            date = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date()
        else:
            date = datetime.now(timezone.utc).date()
        return f"predictions/{date.year}/{date.month:02d}/{date.day:02d}/{request_id}.json"

    def store_prediction(self, result: dict[str, Any]) -> str:
        self.ensure_bucket()
        request_id = str(result["request_id"])
        timestamp = str(result["timestamp"])
        object_name = self.object_path(request_id, timestamp)
        payload = self.serialize_result(result)
        try:
            self.client.put_object(
                self.bucket,
                object_name,
                io.BytesIO(payload),
                length=len(payload),
                content_type="application/json",
            )
        except Exception as exc:
            raise RuntimeError(f"Could not store prediction in MinIO: {exc}") from exc
        logger.info(
            "Prediction stored",
            extra={"bucket": self.bucket, "object": object_name, "request_id": request_id},
        )
        return object_name
